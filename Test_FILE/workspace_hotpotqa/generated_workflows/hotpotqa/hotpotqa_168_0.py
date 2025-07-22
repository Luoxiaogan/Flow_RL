# Workflow ID: hotpotqa_168_0
# Benchmark: hotpotqa
# Data Indices: [1892, 3703, 2199, 3008]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # into smaller steps and trace connections across multiple hops
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace logical connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning
        synthesis_solution = await self.custom(
            instruction="Based on the reasoning above, provide a clear and concise answer to the question."
        )

        # Step 3: Review the synthesized solution to ensure correctness and completeness
        reviewed_solution = await self.review(pre_solution=synthesis_solution)

        # Optional: Generate multiple solutions using different strategies and ensemble them
        # This adds robustness through diversity in reasoning paths
        solution_list = [
            await self.answer_generate(),
            await self.custom(instruction="Solve this by thinking step-by-step and justifying each step."),
            reviewed_solution
        ]
        
        # Step 4: Ensemble the best solution from multiple candidates
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer