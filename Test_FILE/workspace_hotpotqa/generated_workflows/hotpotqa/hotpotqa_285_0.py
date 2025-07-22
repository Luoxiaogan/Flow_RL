# Workflow ID: hotpotqa_285_0
# Benchmark: hotpotqa
# Data Indices: [3824, 293, 2318, 2044]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It breaks down the problem into smaller steps, traces connections across context, and refines the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connecting information across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the initial solution to improve clarity and correctness
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer based on refined solution
        final_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions (e.g., from different reasoning paths) for robustness
        # Generate a few alternative solutions via Custom with varied prompts
        alt_solutions = [
            await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"),
            await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step.")
        ]
        
        # Combine original reviewed solution with alternatives
        all_solutions = [reviewed_solution] + alt_solutions
        ensembled_answer = await self.sc_ensemble(solutions=all_solutions)

        return ensembled_answer