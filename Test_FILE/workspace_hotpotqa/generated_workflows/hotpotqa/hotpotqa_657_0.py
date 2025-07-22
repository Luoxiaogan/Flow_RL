# Workflow ID: hotpotqa_657_0
# Benchmark: hotpotqa
# Data Indices: [2447, 1338, 3885, 3843, 3492]

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
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom to explore multi-hop reasoning via sequential steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Generate alternative reasoning path with a different instruction
        alt_reasoning = await self.custom(
            instruction="Solve this by first identifying all relevant facts, then connecting them logically."
        )

        # Step 4: Ensemble the three solutions (direct, multi-hop, alternate) to select the best one
        solutions = [direct_answer, multi_hop_solution, alt_reasoning]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine the ensembled solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer