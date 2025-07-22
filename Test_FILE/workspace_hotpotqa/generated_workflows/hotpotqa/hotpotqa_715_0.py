# Workflow ID: hotpotqa_715_0
# Benchmark: hotpotqa
# Data Indices: [3132, 1785, 3676, 3428]

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
        This is a robust multi-hop question answering workflow.
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple reasoning paths using different custom instructions
        solutions = []
        
        # Reasoning path 1: Break down into steps with clear explanation
        sol1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solutions.append(sol1)
        
        # Reasoning path 2: Focus on connecting information across different parts of the context
        sol2 = await self.custom(instruction="Focus on connecting information across different parts of the context to form a coherent answer.")
        solutions.append(sol2)
        
        # Reasoning path 3: Use iterative refinement to improve initial answer
        iter_sol = await self.flexible_custom(
            custom_instruction="Start with an initial answer, then verify against the context and refine it iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )
        solutions.append(iter_sol)
        
        # Step 2: Ensemble the solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=solutions)
        
        # Step 3: Final review to ensure correctness and clarity
        final_answer = await self.review(pre_solution=ensemble_solution)
        
        return final_answer