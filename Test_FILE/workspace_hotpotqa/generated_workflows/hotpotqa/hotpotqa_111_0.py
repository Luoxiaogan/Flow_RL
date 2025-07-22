# Workflow ID: hotpotqa_111_0
# Benchmark: hotpotqa
# Data Indices: [1511, 3718, 1915, 3655]

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
        """
        # Step 1: Break down the problem into smaller steps with Custom
        step_by_step_plan = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Use FlexibleCustom with Sequential Multi-Hop to trace connections across context
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Generate a direct answer as a baseline for ensemble
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the solutions to select the best one
        solution_list = [multi_hop_solution, direct_answer]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution