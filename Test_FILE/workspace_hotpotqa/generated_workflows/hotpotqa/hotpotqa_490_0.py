# Workflow ID: hotpotqa_490_0
# Benchmark: hotpotqa
# Data Indices: [2863, 2449, 470, 598]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem,
                                                      reasoning_pattern="sequential",
                                                      steps=["identify_key_entities", "extract_facts", "find_connections", "synthesize_answer"])
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 2: Generate a synthesized answer using Custom with step-by-step instructions
        synthesis = await self.custom(instruction="Based on the extracted facts, synthesize a clear and logical answer.")

        # Step 3: Review the solution for correctness and clarity
        reviewed_solution = await self.review(pre_solution=synthesis)

        # Step 4: Ensemble multiple solutions (simulate by generating a few variations)
        solutions = [multi_hop_solution, synthesis, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer