# Workflow ID: hotpotqa_461_0
# Benchmark: hotpotqa
# Data Indices: [1332, 2553, 1922, 1517]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the answer with a custom operator, and finally reviews it for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_connections_between_entities",
            "trace_reasoning_path",
            "synthesize_final_answer"
        ]
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer from the structured reasoning
        synthesized_answer = await self.custom(instruction="Based on the detailed reasoning steps, generate a clear and concise final answer.")

        # Step 3: Review the synthesized answer to ensure correctness and clarity
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble with initial solution (for robustness) — optional but improves reliability
        solutions = [initial_solution, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer