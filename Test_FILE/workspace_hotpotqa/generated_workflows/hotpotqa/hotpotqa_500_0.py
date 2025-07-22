# Workflow ID: hotpotqa_500_0
# Benchmark: hotpotqa
# Data Indices: [3352, 1984, 2400, 3444]

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
        This is a workflow graph for multi-hop question answering using iterative refinement.
        Starts with an initial answer, then iteratively reviews and refines it based on context.
        """
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use iterative review to refine the answer
        refined_answer = initial_answer
        for _ in range(3):  # Iterative refinement loop (3 iterations)
            revised_answer = await self.review(pre_solution=refined_answer)
            refined_answer = revised_answer

        # Step 3: Ensemble multiple solutions for robustness
        # Generate a few alternative paths using flexible custom reasoning
        solution_list = []
        for i in range(3):
            custom_instruction = "Break down the problem step by step and explain each reasoning step clearly."
            if i == 0:
                solution = await self.custom(instruction=custom_instruction)
            elif i == 1:
                solution = await self.flexible_custom(
                    custom_instruction="Follow a sequential reasoning path: identify key facts, trace connections, then synthesize the answer.",
                    reasoning_pattern="sequential",
                    steps=["identify_facts", "find_connections", "synthesize_answer"]
                )
            else:
                solution = await self.flexible_custom(
                    custom_instruction="Use iterative reasoning: generate hypothesis, verify against context, refine.",
                    reasoning_pattern="iterative",
                    steps=["hypothesis", "verify", "refine"],
                    max_iterations=2
                )
            solution_list.append(solution)

        # Step 4: Ensembling to select best solution
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer