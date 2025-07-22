# Workflow ID: hotpotqa_484_0
# Benchmark: hotpotqa
# Data Indices: [103, 1875, 331, 1109]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem step-by-step.
        """
        # Step 1: Use FlexibleCustom to extract entities and key information from the problem
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps by first extracting key entities and relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Use Custom to refine the extracted information with detailed reasoning
        solution_2 = await self.custom(
            instruction="Now that you have identified key entities and connections, explain how these elements relate to each other in detail to solve the problem."
        )

        # Step 3: Generate an initial answer based on the refined reasoning
        answer = await self.answer_generate()

        # Step 4: Review the generated answer to ensure clarity and correctness
        reviewed_answer = await self.review(pre_solution=answer)

        # Step 5: Ensemble multiple solutions (including original and reviewed) for final accuracy
        ensemble_solutions = [solution_1, solution_2, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_answer