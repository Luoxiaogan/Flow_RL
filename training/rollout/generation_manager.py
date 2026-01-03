"""
Generation Manager for Multi-turn Workflow Generation

Core component for managing multi-turn workflow generation and execution.
Implements the "flatten into independent samples" approach (方案 B).

Reference: ToolOrchestra's LLMGenerationManager
"""

import asyncio
import torch
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from training.rollout.reward_client import RewardClient, ExecutionResult
from training.rollout.prompt_builder import PromptBuilder, AttemptHistory
from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TurnData:
    """Data for a single generation turn"""
    sample_idx: int  # Original sample index
    turn_id: int  # Turn number (0, 1, 2, ...)
    prompt: str  # Input prompt
    response: str  # Model response
    workflow_code: str  # Extracted code (may be empty if extraction failed)
    execution_result: Optional[ExecutionResult] = None
    reward: float = 0.0


@dataclass
class TrajectoryData:
    """Complete trajectory data for a sample"""
    sample_idx: int
    turns: List[TurnData] = field(default_factory=list)
    final_reward: float = 0.0
    success: bool = False


@dataclass
class FlattenedSample:
    """A single flattened sample for VERL training"""
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    response_ids: torch.Tensor
    reward: float
    sample_idx: int
    turn_id: int
    is_final_turn: bool


class GenerationManager:
    """
    Manages multi-turn workflow generation.

    Implements:
    1. Multi-turn generation loop with error repair
    2. Active mask for dynamic stopping
    3. Trajectory collection
    4. Reward computation (trajectory-level)
    5. Flattening into independent samples

    Usage:
        manager = GenerationManager(
            tokenizer=tokenizer,
            reward_server_url="http://localhost:7788",
            max_turns=3
        )

        # In training loop
        flattened = await manager.run_generation_loop(
            prompts=["Generate workflow..."],
            test_problems=[[...], [...], ...],
            benchmarks=["gsm8k", "gsm8k", ...],
            generate_fn=model.generate
        )
    """

    def __init__(
        self,
        tokenizer,
        reward_server_url: str = "http://localhost:7788",
        max_turns: int = 3,
        test_problems_per_workflow: int = 10,
        timeout_per_problem: int = 60
    ):
        """
        Initialize the generation manager.

        Args:
            tokenizer: HuggingFace tokenizer
            reward_server_url: URL of the reward server
            max_turns: Maximum number of generation turns
            test_problems_per_workflow: Number of test problems per workflow
            timeout_per_problem: Timeout per problem in seconds
        """
        self.tokenizer = tokenizer
        self.reward_client = RewardClient(reward_server_url)
        self.prompt_builder = PromptBuilder()
        self.max_turns = max_turns
        self.test_problems_per_workflow = test_problems_per_workflow
        self.timeout_per_problem = timeout_per_problem

    async def run_generation_loop(
        self,
        prompts: List[str],
        test_problems: List[List[Dict[str, Any]]],
        benchmarks: List[str],
        generate_fn,  # Callable that takes prompts and returns responses
        global_step: int = 0
    ) -> Dict[str, Any]:
        """
        Run the multi-turn generation loop.

        Args:
            prompts: List of initial prompts (one per sample)
            test_problems: List of test problem lists (one list per sample)
            benchmarks: List of benchmark names (one per sample)
            generate_fn: Function to generate responses from prompts
            global_step: Current training step (for logging)

        Returns:
            Dict with:
                - flattened_samples: List of FlattenedSample
                - trajectories: List of TrajectoryData
                - stats: Dict with statistics
        """
        batch_size = len(prompts)

        # Initialize active mask (True = still generating)
        active_mask = torch.ones(batch_size, dtype=torch.bool)

        # Initialize histories for each sample
        histories: List[List[AttemptHistory]] = [[] for _ in range(batch_size)]

        # Collect all turns
        all_turns: List[TurnData] = []

        # Base prompts for repair
        base_prompts = prompts.copy()

        for turn in range(self.max_turns):
            if not active_mask.any():
                logger.info(f"All samples completed at turn {turn}")
                break

            logger.info(
                f"Turn {turn}: {active_mask.sum().item()}/{batch_size} samples active"
            )

            # 1. Build prompts (including repair prompts for failed samples)
            current_prompts = self._build_current_prompts(
                base_prompts=base_prompts,
                histories=histories,
                active_mask=active_mask
            )

            # 2. Generate responses
            responses = await self._generate_responses(
                prompts=current_prompts,
                active_mask=active_mask,
                generate_fn=generate_fn
            )

            # 3. Extract workflow code from responses
            workflow_codes = self._extract_workflows(responses, active_mask)

            # 4. Execute workflows and get results
            execution_results = await self._execute_workflows(
                workflow_codes=workflow_codes,
                test_problems=test_problems,
                benchmarks=benchmarks,
                active_mask=active_mask
            )

            # 5. Collect turn data
            turn_data = self._collect_turn_data(
                sample_indices=list(range(batch_size)),
                turn_id=turn,
                prompts=current_prompts,
                responses=responses,
                workflow_codes=workflow_codes,
                execution_results=execution_results,
                active_mask=active_mask
            )
            all_turns.extend(turn_data)

            # 6. Update histories and active mask
            self._update_state(
                histories=histories,
                workflow_codes=workflow_codes,
                execution_results=execution_results,
                active_mask=active_mask
            )

        # 7. Build trajectories
        trajectories = self._build_trajectories(
            batch_size=batch_size,
            all_turns=all_turns,
            histories=histories
        )

        # 8. Compute rewards
        self._compute_rewards(trajectories)

        # 9. Flatten into samples
        flattened_samples = self._flatten_trajectories(trajectories)

        # 10. Compute statistics
        stats = self._compute_stats(trajectories, all_turns)

        logger.info(
            f"Generation complete: {stats['success_rate']:.1%} success rate, "
            f"{stats['avg_turns']:.1f} avg turns, "
            f"{stats['total_samples']} total samples"
        )

        return {
            "flattened_samples": flattened_samples,
            "trajectories": trajectories,
            "stats": stats
        }

    def _build_current_prompts(
        self,
        base_prompts: List[str],
        histories: List[List[AttemptHistory]],
        active_mask: torch.Tensor
    ) -> List[Optional[str]]:
        """Build prompts for current turn."""
        prompts = []
        for i in range(len(base_prompts)):
            if not active_mask[i]:
                prompts.append(None)
            else:
                prompt = self.prompt_builder.build_prompt_from_history(
                    base_prompt=base_prompts[i],
                    history=histories[i]
                )
                prompts.append(prompt)
        return prompts

    async def _generate_responses(
        self,
        prompts: List[Optional[str]],
        active_mask: torch.Tensor,
        generate_fn
    ) -> List[Optional[str]]:
        """Generate responses using the provided generate function."""
        # Filter active prompts
        active_prompts = [p for p, m in zip(prompts, active_mask) if m and p]

        if not active_prompts:
            return [None] * len(prompts)

        # Generate
        if asyncio.iscoroutinefunction(generate_fn):
            active_responses = await generate_fn(active_prompts)
        else:
            active_responses = generate_fn(active_prompts)

        # Map back to full list
        responses = []
        active_idx = 0
        for i, (prompt, mask) in enumerate(zip(prompts, active_mask)):
            if mask and prompt:
                responses.append(active_responses[active_idx])
                active_idx += 1
            else:
                responses.append(None)

        return responses

    def _extract_workflows(
        self,
        responses: List[Optional[str]],
        active_mask: torch.Tensor
    ) -> List[Optional[str]]:
        """Extract workflow code from responses."""
        codes = []
        for i, (resp, mask) in enumerate(zip(responses, active_mask)):
            if not mask or resp is None:
                codes.append(None)
            else:
                code = self.prompt_builder.extract_code_from_response(resp)
                codes.append(code)
        return codes

    async def _execute_workflows(
        self,
        workflow_codes: List[Optional[str]],
        test_problems: List[List[Dict[str, Any]]],
        benchmarks: List[str],
        active_mask: torch.Tensor
    ) -> List[Optional[ExecutionResult]]:
        """Execute workflows and get results."""
        results = []

        # Create tasks for active workflows
        tasks = []
        task_indices = []

        for i, (code, problems, bench, mask) in enumerate(
            zip(workflow_codes, test_problems, benchmarks, active_mask)
        ):
            if not mask or code is None:
                results.append(None)
            else:
                task = self.reward_client.execute_workflow(
                    workflow_code=code,
                    test_problems=problems[:self.test_problems_per_workflow],
                    benchmark=bench,
                    timeout=self.timeout_per_problem
                )
                tasks.append(task)
                task_indices.append(i)
                results.append(None)  # Placeholder

        # Execute in parallel
        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            for idx, result in zip(task_indices, task_results):
                if isinstance(result, Exception):
                    results[idx] = ExecutionResult(
                        success=False,
                        score=0.0,
                        error=str(result)
                    )
                else:
                    results[idx] = result

        return results

    def _collect_turn_data(
        self,
        sample_indices: List[int],
        turn_id: int,
        prompts: List[Optional[str]],
        responses: List[Optional[str]],
        workflow_codes: List[Optional[str]],
        execution_results: List[Optional[ExecutionResult]],
        active_mask: torch.Tensor
    ) -> List[TurnData]:
        """Collect data for this turn."""
        turn_data = []
        for i in sample_indices:
            if not active_mask[i]:
                continue

            turn_data.append(TurnData(
                sample_idx=i,
                turn_id=turn_id,
                prompt=prompts[i] or "",
                response=responses[i] or "",
                workflow_code=workflow_codes[i] or "",
                execution_result=execution_results[i],
                reward=0.0  # Will be set later
            ))

        return turn_data

    def _update_state(
        self,
        histories: List[List[AttemptHistory]],
        workflow_codes: List[Optional[str]],
        execution_results: List[Optional[ExecutionResult]],
        active_mask: torch.Tensor
    ):
        """Update histories and active mask based on results."""
        for i in range(len(histories)):
            if not active_mask[i]:
                continue

            code = workflow_codes[i]
            result = execution_results[i]

            if code is None:
                # Failed to extract code
                histories[i].append(AttemptHistory(
                    workflow_code="",
                    result="error",
                    error="Failed to extract code from response"
                ))
                # Keep trying
                continue

            if result is None:
                # No execution result
                histories[i].append(AttemptHistory(
                    workflow_code=code,
                    result="error",
                    error="No execution result"
                ))
                continue

            if result.success and result.score >= 1.0:
                # Perfect score - done
                histories[i].append(AttemptHistory(
                    workflow_code=code,
                    result="success",
                    accuracy=result.score
                ))
                active_mask[i] = False

            elif result.success:
                # Partial success - record for potential improvement
                histories[i].append(AttemptHistory(
                    workflow_code=code,
                    result="success",  # Execution succeeded
                    accuracy=result.score,
                    failed_problems=result.failed_problems
                ))
                # Stop if score is good enough (>= 80%)
                if result.score >= 0.8:
                    active_mask[i] = False

            else:
                # Execution error - try to repair
                histories[i].append(AttemptHistory(
                    workflow_code=code,
                    result="error",
                    error=result.error,
                    traceback=result.traceback
                ))

    def _build_trajectories(
        self,
        batch_size: int,
        all_turns: List[TurnData],
        histories: List[List[AttemptHistory]]
    ) -> List[TrajectoryData]:
        """Build trajectory objects from collected turns."""
        trajectories = [
            TrajectoryData(sample_idx=i)
            for i in range(batch_size)
        ]

        # Assign turns to trajectories
        for turn in all_turns:
            trajectories[turn.sample_idx].turns.append(turn)

        # Set final status
        for i, (traj, history) in enumerate(zip(trajectories, histories)):
            if history and history[-1].result == "success":
                traj.success = True
                traj.final_reward = history[-1].accuracy or 0.0
            else:
                traj.success = False
                traj.final_reward = 0.0

        return trajectories

    def _compute_rewards(self, trajectories: List[TrajectoryData]):
        """
        Compute rewards for all turns.

        Uses trajectory-level reward: all turns in a trajectory
        get the same final reward.
        """
        for traj in trajectories:
            for turn in traj.turns:
                turn.reward = traj.final_reward

    def _flatten_trajectories(
        self,
        trajectories: List[TrajectoryData]
    ) -> List[Dict[str, Any]]:
        """
        Flatten trajectories into independent samples for VERL.

        Each turn becomes a separate training sample with:
        - input: the prompt
        - output: the response
        - reward: trajectory-level reward
        """
        samples = []

        for traj in trajectories:
            num_turns = len(traj.turns)

            for turn in traj.turns:
                # Tokenize
                input_encoding = self.tokenizer(
                    turn.prompt,
                    return_tensors="pt",
                    padding=False,
                    truncation=True
                )

                response_encoding = self.tokenizer(
                    turn.response,
                    return_tensors="pt",
                    padding=False,
                    truncation=True
                )

                samples.append({
                    "input_ids": input_encoding.input_ids.squeeze(0),
                    "attention_mask": input_encoding.attention_mask.squeeze(0),
                    "response_ids": response_encoding.input_ids.squeeze(0),
                    "reward": turn.reward,
                    "sample_idx": turn.sample_idx,
                    "turn_id": turn.turn_id,
                    "is_final_turn": turn.turn_id == num_turns - 1,
                    "workflow_code": turn.workflow_code,
                    "success": traj.success
                })

        return samples

    def _compute_stats(
        self,
        trajectories: List[TrajectoryData],
        all_turns: List[TurnData]
    ) -> Dict[str, Any]:
        """Compute statistics for logging."""
        num_success = sum(1 for t in trajectories if t.success)
        total_turns = len(all_turns)
        avg_turns = total_turns / len(trajectories) if trajectories else 0

        rewards = [t.final_reward for t in trajectories]
        avg_reward = np.mean(rewards) if rewards else 0.0

        return {
            "success_count": num_success,
            "total_count": len(trajectories),
            "success_rate": num_success / len(trajectories) if trajectories else 0,
            "total_samples": total_turns,
            "avg_turns": avg_turns,
            "avg_reward": avg_reward,
            "max_reward": max(rewards) if rewards else 0,
            "min_reward": min(rewards) if rewards else 0
        }

    async def close(self):
        """Close resources."""
        await self.reward_client.close()
