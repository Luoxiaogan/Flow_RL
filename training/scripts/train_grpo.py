#!/usr/bin/env python
"""
GRPO Training Entry Script

Train a workflow generation model using GRPO.

Usage:
    python training/scripts/train_grpo.py --config training/recipe/grpo/config.yaml
"""

import os
import sys
import yaml
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from training.recipe.grpo.trainer import WorkflowGRPOTrainer, GRPOConfig
from src.core.logger import setup_logger, get_logger

logger = get_logger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_training_data(config: dict) -> list:
    """
    Load training data.

    For now, returns dummy data. Replace with actual data loading.
    """
    # TODO: Implement actual data loading
    # This should load prompts and test problems from your dataset

    logger.info("Loading training data...")

    # Dummy data for testing
    dummy_data = []
    for i in range(10):
        dummy_data.append({
            "prompt": f"""You are an expert Python programmer.
Create a workflow function to solve math word problems.

Example problem: If John has 5 apples and gives 2 to Mary, how many does he have left?
Answer: 3

Generate a Python function named 'solve' that takes a problem dict with 'question' key.
""",
            "test_problems": [
                {"id": f"{i}_0", "question": "What is 2+3?", "answer": "5"},
                {"id": f"{i}_1", "question": "What is 10-4?", "answer": "6"},
                {"id": f"{i}_2", "question": "What is 3*4?", "answer": "12"},
            ],
            "benchmark": "gsm8k"
        })

    logger.info(f"Loaded {len(dummy_data)} training examples")
    return dummy_data


def main():
    parser = argparse.ArgumentParser(description="GRPO Training for Workflow Generation")
    parser.add_argument(
        "--config",
        type=str,
        default="training/recipe/grpo/config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name or path (overrides config)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Output directory (overrides config)"
    )
    parser.add_argument(
        "--reward_server_url",
        type=str,
        default=None,
        help="Reward server URL (overrides config)"
    )
    parser.add_argument(
        "--num_epochs",
        type=int,
        default=None,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger("grpo_training", level=log_level)

    logger.info("=" * 60)
    logger.info("GRPO Training for Workflow Generation")
    logger.info("=" * 60)

    # Load config
    config_path = project_root / args.config
    if config_path.exists():
        config = load_config(str(config_path))
        logger.info(f"Loaded config from {config_path}")
    else:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        config = {}

    # Override with command line args
    model_name = args.model or config.get("model", {}).get("name_or_path", "Qwen/Qwen2.5-7B-Instruct")
    output_dir = args.output_dir or config.get("paths", {}).get("output_dir", "./outputs")
    reward_server_url = args.reward_server_url or config.get("reward_server", {}).get("url", "http://localhost:7788")
    num_epochs = args.num_epochs or config.get("training", {}).get("num_epochs", 3)

    logger.info(f"Model: {model_name}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Reward server: {reward_server_url}")
    logger.info(f"Epochs: {num_epochs}")

    # Load model and tokenizer
    logger.info("Loading model and tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto"
    )

    logger.info(f"Model loaded: {model.config.name_or_path}")
    logger.info(f"Model device: {model.device}")

    # Create trainer config
    trainer_config = GRPOConfig(
        model_name_or_path=model_name,
        reward_server_url=reward_server_url,
        max_turns=config.get("generation", {}).get("max_turns", 3),
        test_problems_per_workflow=config.get("generation", {}).get("test_problems_per_workflow", 10),
        timeout_per_problem=config.get("generation", {}).get("timeout_per_problem", 60),
        batch_size=config.get("training", {}).get("batch_size", 8),
        num_rollouts_per_prompt=config.get("training", {}).get("num_rollouts_per_prompt", 4),
        learning_rate=config.get("training", {}).get("learning_rate", 1e-5),
        max_grad_norm=config.get("training", {}).get("max_grad_norm", 1.0),
        warmup_steps=config.get("training", {}).get("warmup_steps", 100),
        kl_coef=config.get("grpo", {}).get("kl_coef", 0.1),
        clip_range=config.get("grpo", {}).get("clip_range", 0.2),
        gamma=config.get("grpo", {}).get("gamma", 1.0),
        log_interval=config.get("logging", {}).get("log_interval", 10),
        save_interval=config.get("logging", {}).get("save_interval", 100),
        eval_interval=config.get("logging", {}).get("eval_interval", 50),
        output_dir=output_dir,
        checkpoint_dir=config.get("paths", {}).get("checkpoint_dir", "./checkpoints")
    )

    # Create trainer
    logger.info("Creating trainer...")
    trainer = WorkflowGRPOTrainer(
        model=model,
        tokenizer=tokenizer,
        config=trainer_config
    )

    # Load training data
    train_data = load_training_data(config)

    # Train
    logger.info("Starting training...")
    try:
        trainer.train(
            train_data=train_data,
            num_epochs=num_epochs
        )
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        trainer.save_checkpoint(final=True)
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise
    finally:
        # Cleanup
        import asyncio
        asyncio.run(trainer.close())

    logger.info("Training complete!")


if __name__ == "__main__":
    main()
