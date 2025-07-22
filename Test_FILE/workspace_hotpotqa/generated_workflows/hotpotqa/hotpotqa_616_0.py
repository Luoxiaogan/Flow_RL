# Workflow ID: hotpotqa_616_0
# Benchmark: hotpotqa
# Data Indices: [2022, 3365, 2393, 1657, 698]

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
        It uses flexible custom reasoning to break down the problem into steps,
        then synthesizes the answer with iterative refinement and ensemble selection.
        """
        # Step 1: Use FlexibleCustom to extract entities and find connections in a structured way
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using sequential reasoning.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the initial solution for potential errors or omissions
        reviewed_solution = await self.review(pre_solution=multi_hop_solution)

        # Step 3: Generate an alternative direct answer for ensembling
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the two solutions to select the best one
        final_answer = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_answer