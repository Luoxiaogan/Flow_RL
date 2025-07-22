# Workflow ID: hotpotqa_797_0
# Benchmark: hotpotqa
# Data Indices: [3790, 1949, 178, 3681, 3764]

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
        It first breaks down the problem step-by-step, then generates an answer, reviews it, and finally ensembles with alternative solutions if needed.
        """
        # Step 1: Use FlexibleCustom to perform sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Review the generated answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=answer)

        # Step 4: Optionally generate alternative solutions for ensemble (if multiple paths exist)
        alt_solutions = [
            await self.custom(instruction="Solve this by focusing on the connections between entities in the context."),
            await self.custom(instruction="Think step-by-step: identify what must be known first, then build toward the final answer.")
        ]

        # Step 5: Ensemble the original reviewed answer with alternatives to select the best one
        final_solution = await self.sc_ensemble(solutions=[reviewed_answer] + alt_solutions)

        return final_solution