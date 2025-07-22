# Workflow ID: hotpotqa_826_0
# Benchmark: hotpotqa
# Data Indices: [72, 2444, 1660, 3000]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        # and trace connections between entities or concepts in the context
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_intermediate_connections",
            "synthesize_final_answer"
        ]
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities, extracting relevant facts, finding connections between them, and finally synthesizing the answer.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to refine the synthesized answer with clear reasoning
        refined_solution = await self.custom(
            instruction="Explain your reasoning step-by-step, ensuring each part of the solution logically connects to the next. Be precise and avoid unnecessary assumptions."
        )

        # Step 3: Use Review to validate and improve the solution based on its internal logic
        validated_solution = await self.review(pre_solution=refined_solution)

        # Step 4: Optionally, generate multiple candidate solutions and ensemble them for robustness
        # We generate two solutions using different prompts to increase diversity
        solution1 = await self.answer_generate()
        solution2 = await self.custom(instruction="Solve this by breaking it into smaller logical steps and explaining each step clearly.")
        ensemble_candidates = [solution1, solution2]
        final_solution = await self.sc_ensemble(solutions=ensemble_candidates)

        # Return the most reliable solution after review and ensemble
        return final_solution