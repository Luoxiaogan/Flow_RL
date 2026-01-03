"""
Workflow GRPO Trainer

GRPO (Group Relative Policy Optimization) trainer for workflow generation.
Integrates with the GenerationManager for multi-turn rollouts.

Reference: ToolOrchestra's GRPO implementation
"""

import os
import asyncio
import torch
import numpy as np
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path

from training.rollout.generation_manager import GenerationManager
from training.rollout.reward_client import RewardClient
from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GRPOConfig:
    """Configuration for GRPO training."""
    # Model
    model_name_or_path: str = "Qwen/Qwen2.5-7B-Instruct"

    # Reward server
    reward_server_url: str = "http://localhost:7788"

    # Generation
    max_turns: int = 3
    test_problems_per_workflow: int = 10
    timeout_per_problem: int = 60

    # Training
    batch_size: int = 8
    num_rollouts_per_prompt: int = 4
    learning_rate: float = 1e-5
    max_grad_norm: float = 1.0
    warmup_steps: int = 100

    # GRPO specific
    kl_coef: float = 0.1
    clip_range: float = 0.2
    gamma: float = 1.0

    # Logging
    log_interval: int = 10
    save_interval: int = 100
    eval_interval: int = 50

    # Paths
    output_dir: str = "./outputs"
    checkpoint_dir: str = "./checkpoints"


class WorkflowGRPOTrainer:
    """
    GRPO Trainer for workflow generation.

    Implements the training loop that:
    1. Generates workflows using the policy model
    2. Executes workflows and computes rewards
    3. Updates the policy using GRPO

    Usage:
        trainer = WorkflowGRPOTrainer(
            model=model,
            tokenizer=tokenizer,
            config=GRPOConfig()
        )
        trainer.train(train_dataset, eval_dataset)
    """

    def __init__(
        self,
        model,
        tokenizer,
        config: GRPOConfig,
        ref_model=None,
        optimizer=None,
        scheduler=None
    ):
        """
        Initialize the trainer.

        Args:
            model: Policy model (HuggingFace model)
            tokenizer: Tokenizer
            config: Training configuration
            ref_model: Reference model for KL penalty (optional)
            optimizer: Optimizer (creates default if None)
            scheduler: Learning rate scheduler (optional)
        """
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.ref_model = ref_model
        self.optimizer = optimizer
        self.scheduler = scheduler

        # Initialize generation manager
        self.generation_manager = GenerationManager(
            tokenizer=tokenizer,
            reward_server_url=config.reward_server_url,
            max_turns=config.max_turns,
            test_problems_per_workflow=config.test_problems_per_workflow,
            timeout_per_problem=config.timeout_per_problem
        )

        # Setup optimizer if not provided
        if self.optimizer is None:
            self.optimizer = torch.optim.AdamW(
                self.model.parameters(),
                lr=config.learning_rate
            )

        # Training state
        self.global_step = 0
        self.epoch = 0

        # Setup output directories
        self.output_dir = Path(config.output_dir)
        self.checkpoint_dir = Path(config.checkpoint_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    async def generate_rollouts(
        self,
        prompts: List[str],
        test_problems: List[List[Dict[str, Any]]],
        benchmarks: List[str]
    ) -> Dict[str, Any]:
        """
        Generate rollouts using the policy model.

        Args:
            prompts: List of prompts
            test_problems: List of test problem lists
            benchmarks: List of benchmark names

        Returns:
            Rollout results from generation manager
        """
        # Define generate function using the model
        def generate_fn(active_prompts: List[str]) -> List[str]:
            # Tokenize prompts
            inputs = self.tokenizer(
                active_prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=2048
            ).to(self.model.device)

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )

            # Decode
            responses = []
            for i, output in enumerate(outputs):
                input_len = inputs.input_ids[i].shape[0]
                response = self.tokenizer.decode(
                    output[input_len:],
                    skip_special_tokens=True
                )
                responses.append(response)

            return responses

        # Run generation loop
        return await self.generation_manager.run_generation_loop(
            prompts=prompts,
            test_problems=test_problems,
            benchmarks=benchmarks,
            generate_fn=generate_fn,
            global_step=self.global_step
        )

    def compute_advantages(
        self,
        rewards: List[float],
        sample_indices: List[int]
    ) -> torch.Tensor:
        """
        Compute GRPO advantages.

        GRPO uses intra-example normalization:
        For samples from the same prompt, normalize rewards
        within that group.

        Args:
            rewards: List of rewards for each sample
            sample_indices: Original sample indices

        Returns:
            Tensor of advantages
        """
        rewards = torch.tensor(rewards, dtype=torch.float32)
        indices = torch.tensor(sample_indices, dtype=torch.long)

        # Group rewards by sample index
        unique_indices = indices.unique()
        advantages = torch.zeros_like(rewards)

        for idx in unique_indices:
            mask = indices == idx
            group_rewards = rewards[mask]

            # Normalize within group
            mean = group_rewards.mean()
            std = group_rewards.std() + 1e-8
            advantages[mask] = (group_rewards - mean) / std

        return advantages

    def compute_policy_loss(
        self,
        log_probs: torch.Tensor,
        ref_log_probs: torch.Tensor,
        advantages: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute GRPO policy loss.

        Args:
            log_probs: Log probabilities from policy
            ref_log_probs: Log probabilities from reference model
            advantages: Computed advantages

        Returns:
            Policy loss tensor
        """
        # KL divergence
        kl = log_probs - ref_log_probs

        # Policy gradient loss with KL penalty
        pg_loss = -advantages * log_probs
        kl_loss = self.config.kl_coef * kl

        loss = (pg_loss + kl_loss).mean()
        return loss

    def train_step(
        self,
        batch: Dict[str, torch.Tensor]
    ) -> Dict[str, float]:
        """
        Perform a single training step.

        Args:
            batch: Batch of training data

        Returns:
            Dict with loss and metrics
        """
        self.model.train()

        input_ids = batch["input_ids"].to(self.model.device)
        attention_mask = batch["attention_mask"].to(self.model.device)
        response_ids = batch["response_ids"].to(self.model.device)
        advantages = batch["advantages"].to(self.model.device)

        # Forward pass
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=response_ids
        )

        # Get log probs
        log_probs = -outputs.loss  # Simplified

        # Reference model log probs
        if self.ref_model is not None:
            with torch.no_grad():
                ref_outputs = self.ref_model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=response_ids
                )
                ref_log_probs = -ref_outputs.loss
        else:
            ref_log_probs = log_probs.detach()

        # Compute loss
        loss = self.compute_policy_loss(log_probs, ref_log_probs, advantages)

        # Backward
        self.optimizer.zero_grad()
        loss.backward()

        # Gradient clipping
        if self.config.max_grad_norm > 0:
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.max_grad_norm
            )

        self.optimizer.step()

        if self.scheduler is not None:
            self.scheduler.step()

        return {
            "loss": loss.item(),
            "log_probs": log_probs.mean().item(),
        }

    async def train_epoch(
        self,
        train_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Train for one epoch.

        Args:
            train_data: List of training examples with prompts and test problems

        Returns:
            Dict with epoch metrics
        """
        total_loss = 0.0
        num_batches = 0

        # Process in batches
        for i in range(0, len(train_data), self.config.batch_size):
            batch_data = train_data[i:i + self.config.batch_size]

            # Extract prompts and problems
            prompts = [d["prompt"] for d in batch_data]
            test_problems = [d["test_problems"] for d in batch_data]
            benchmarks = [d.get("benchmark", "gsm8k") for d in batch_data]

            # Generate rollouts
            rollout_result = await self.generate_rollouts(
                prompts=prompts,
                test_problems=test_problems,
                benchmarks=benchmarks
            )

            # Get flattened samples
            samples = rollout_result["flattened_samples"]

            if not samples:
                continue

            # Compute advantages
            rewards = [s["reward"] for s in samples]
            sample_indices = [s["sample_idx"] for s in samples]
            advantages = self.compute_advantages(rewards, sample_indices)

            # Prepare batch
            batch = {
                "input_ids": torch.stack([s["input_ids"] for s in samples]),
                "attention_mask": torch.stack([s["attention_mask"] for s in samples]),
                "response_ids": torch.stack([s["response_ids"] for s in samples]),
                "advantages": advantages
            }

            # Training step
            metrics = self.train_step(batch)
            total_loss += metrics["loss"]
            num_batches += 1

            self.global_step += 1

            # Logging
            if self.global_step % self.config.log_interval == 0:
                logger.info(
                    f"Step {self.global_step}: "
                    f"loss={metrics['loss']:.4f}, "
                    f"avg_reward={np.mean(rewards):.4f}"
                )

            # Saving
            if self.global_step % self.config.save_interval == 0:
                self.save_checkpoint()

        return {
            "epoch_loss": total_loss / max(num_batches, 1),
            "num_batches": num_batches
        }

    def train(
        self,
        train_data: List[Dict[str, Any]],
        num_epochs: int = 1,
        eval_data: List[Dict[str, Any]] = None
    ):
        """
        Main training loop.

        Args:
            train_data: Training data
            num_epochs: Number of epochs
            eval_data: Optional evaluation data
        """
        logger.info(f"Starting training for {num_epochs} epochs")
        logger.info(f"Training samples: {len(train_data)}")

        for epoch in range(num_epochs):
            self.epoch = epoch
            logger.info(f"Epoch {epoch + 1}/{num_epochs}")

            # Run training epoch
            metrics = asyncio.run(self.train_epoch(train_data))

            logger.info(
                f"Epoch {epoch + 1} complete: "
                f"loss={metrics['epoch_loss']:.4f}"
            )

            # Evaluation
            if eval_data and (epoch + 1) % self.config.eval_interval == 0:
                eval_metrics = asyncio.run(self.evaluate(eval_data))
                logger.info(f"Evaluation: {eval_metrics}")

        # Final save
        self.save_checkpoint(final=True)
        logger.info("Training complete!")

    async def evaluate(
        self,
        eval_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Evaluate on validation data.

        Args:
            eval_data: Evaluation data

        Returns:
            Evaluation metrics
        """
        self.model.eval()
        all_rewards = []

        with torch.no_grad():
            for data in eval_data[:10]:  # Limit for speed
                rollout = await self.generate_rollouts(
                    prompts=[data["prompt"]],
                    test_problems=[data["test_problems"]],
                    benchmarks=[data.get("benchmark", "gsm8k")]
                )

                for sample in rollout["flattened_samples"]:
                    all_rewards.append(sample["reward"])

        return {
            "avg_reward": np.mean(all_rewards) if all_rewards else 0.0,
            "max_reward": max(all_rewards) if all_rewards else 0.0,
            "num_samples": len(all_rewards)
        }

    def save_checkpoint(self, final: bool = False):
        """Save model checkpoint."""
        suffix = "final" if final else f"step_{self.global_step}"
        checkpoint_path = self.checkpoint_dir / f"checkpoint_{suffix}"

        logger.info(f"Saving checkpoint to {checkpoint_path}")

        self.model.save_pretrained(checkpoint_path)
        self.tokenizer.save_pretrained(checkpoint_path)

        # Save training state
        state = {
            "global_step": self.global_step,
            "epoch": self.epoch,
            "optimizer_state": self.optimizer.state_dict(),
        }
        torch.save(state, checkpoint_path / "trainer_state.pt")

    def load_checkpoint(self, checkpoint_path: str):
        """Load model checkpoint."""
        logger.info(f"Loading checkpoint from {checkpoint_path}")

        checkpoint_path = Path(checkpoint_path)

        # Load training state
        state_path = checkpoint_path / "trainer_state.pt"
        if state_path.exists():
            state = torch.load(state_path)
            self.global_step = state["global_step"]
            self.epoch = state["epoch"]
            self.optimizer.load_state_dict(state["optimizer_state"])

    async def close(self):
        """Cleanup resources."""
        await self.generation_manager.close()
