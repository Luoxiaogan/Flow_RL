# Workflow ID: hotpotqa_670_0
# Benchmark: hotpotqa
# Data Indices: [1864, 2621, 1383, 1014, 514]

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
        # and extract relevant facts from the context in a structured way
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and identify key entities, relationships, and connections across the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on the extracted facts
        synthesis = await self.custom(
            instruction="Using the information gathered above, generate a clear and concise answer to the question. Reason step-by-step."
        )

        # Step 3: Review the synthesized answer for accuracy and completeness
        reviewed_answer = await self.review(pre_solution=synthesis)

        # Step 4: Generate an alternative direct answer using AnswerGenerate for ensemble
        direct_answer = await self.answer_generate()

        # Step 5: Ensemble the two solutions to select the best one
        final_answer = await self.sc_ensemble(solutions=[reviewed_answer, direct_answer])

        return final_answer