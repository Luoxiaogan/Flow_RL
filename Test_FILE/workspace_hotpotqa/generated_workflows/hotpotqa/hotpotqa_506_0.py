# Workflow ID: hotpotqa_506_0
# Benchmark: hotpotqa
# Data Indices: [3551, 2686, 2707, 3421, 325]

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
        This is a workflow graph for multi-hop question answering.
        It uses FlexibleCustom with sequential reasoning to break down the problem into key steps.
        """
        # Step 1: Use flexible custom to extract entities and key information from the problem
        solution_1 = await self.flexible_custom(
            custom_instruction="Extract all relevant entities, facts, and relationships in the problem.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "identify_bridges"]
        )

        # Step 2: Use flexible custom to trace connections between extracted entities
        solution_2 = await self.flexible_custom(
            custom_instruction="Trace logical connections between the extracted entities to form a reasoning path.",
            reasoning_pattern="sequential",
            steps=["find_connections", "trace_reasoning_path"]
        )

        # Step 3: Synthesize the final answer using the connected reasoning path
        solution_3 = await self.flexible_custom(
            custom_instruction="Synthesize the final answer based on the traced reasoning path.",
            reasoning_pattern="sequential",
            steps=["synthesize_answer"]
        )

        # Optional: Ensemble multiple solutions if more than one exists (e.g., from different reasoning paths)
        solutions = [solution_1, solution_2, solution_3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Final review step to refine the ensemble result
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution