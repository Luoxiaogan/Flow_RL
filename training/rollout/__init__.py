"""
Training Rollout Module

This module contains components for:
- Reward client for communicating with reward server
- Multi-turn generation management
- Prompt building for generation and repair
- Trajectory collection for VERL training
"""

from training.rollout.reward_client import RewardClient, ExecutionResult
from training.rollout.prompt_builder import PromptBuilder, AttemptHistory
from training.rollout.generation_manager import (
    GenerationManager,
    TurnData,
    TrajectoryData,
    FlattenedSample
)

__all__ = [
    # Reward client
    "RewardClient",
    "ExecutionResult",
    # Prompt builder
    "PromptBuilder",
    "AttemptHistory",
    # Generation manager
    "GenerationManager",
    "TurnData",
    "TrajectoryData",
    "FlattenedSample",
]
