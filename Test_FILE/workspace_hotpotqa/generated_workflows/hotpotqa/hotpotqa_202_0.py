# Workflow ID: hotpotqa_202_0
# Benchmark: hotpotqa
# Data Indices: [3451, 1255, 1204, 3864, 752]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer,
        and finally validates it through review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem and extract key facts
        reasoning_steps = ["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        intermediate_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on identifying key entities and tracing how they connect across multiple pieces of information.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear, structured answer based on the extracted reasoning
        synthesis_instruction = "Based on the reasoning above, generate a concise and accurate answer that directly addresses the question."
        synthesized_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Review the synthesized answer to ensure accuracy and clarity
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Optional: Ensemble with another solution from a different reasoning path (e.g., iterative) to improve robustness
        # Generate an alternative solution using iterative refinement
        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, then refine it iteratively by checking consistency with the context.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )

        # Combine both solutions into a list for ensemble
        solutions = [reviewed_answer, iterative_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer