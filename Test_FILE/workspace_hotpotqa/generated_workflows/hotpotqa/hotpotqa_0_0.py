# Workflow ID: hotpotqa_0_0
# Benchmark: hotpotqa
# Data Indices: [3656, 1762, 2320, 3930, 2254]

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
        This is a robust workflow graph for multi-hop question answering.
        It generates multiple reasoning paths using different Custom instructions,
        then ensembles the best solution, and finally reviews it for correctness.
        """
        # Step 1: Generate multiple reasoning paths via different custom instructions
        solutions = []
        
        # Reasoning path 1: Break down into smaller steps
        sol1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solutions.append(sol1)
        
        # Reasoning path 2: Focus on connecting information across parts of the context
        sol2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step, focusing on linking different pieces of evidence.")
        solutions.append(sol2)
        
        # Reasoning path 3: Use iterative refinement to improve answer quality
        sol3 = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, then verify facts and refine your answer iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )
        solutions.append(sol3)
        
        # Step 2: Ensemble the top solutions to get the most reliable answer
        ensemble_solution = await self.sc_ensemble(solutions=solutions)
        
        # Step 3: Final review to ensure accuracy and completeness
        final_answer = await self.review(pre_solution=ensemble_solution)
        
        return final_answer