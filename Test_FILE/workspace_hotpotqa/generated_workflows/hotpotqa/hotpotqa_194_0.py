# Workflow ID: hotpotqa_194_0
# Benchmark: hotpotqa
# Data Indices: [2551, 741, 2007, 2487]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        Finally, it reviews the solution for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem and extract relevant facts
        fact_extraction = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and identify key facts needed to answer it.",
            reasoning_pattern="sequential",
            steps=["identify_question", "extract_facts", "find_connections", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear and structured answer based on extracted facts
        synthesis = await self.custom(
            instruction="Based on the identified facts and connections, generate a detailed and logically structured answer."
        )

        # Step 3: Ensemble multiple solutions (if we had more than one) — currently just one, but ready for expansion
        solution_list = [synthesis]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 4: Review the final solution for coherence and correctness
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer