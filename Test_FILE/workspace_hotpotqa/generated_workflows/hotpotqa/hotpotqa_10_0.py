# Workflow ID: hotpotqa_10_0
# Benchmark: hotpotqa
# Data Indices: [720, 821, 1032, 1031, 3578]

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
        # Step 1: Generate multiple reasoning paths via Custom with different step-by-step prompts
        solutions = []
        custom_instructions = [
            "Break down the problem into smaller steps and explain the reasoning behind each step.",
            "Solve this by identifying key entities and tracing connections between them.",
            "First identify all relevant facts from the context, then synthesize an answer."
        ]
        
        for instruction in custom_instructions:
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Ensemble the best solution from multiple reasoning paths
        ensemble_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to refine the ensemble solution
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer