# Workflow ID: hotpotqa_237_0
# Benchmark: hotpotqa
# Data Indices: [2889, 156, 121, 3104]

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
        It uses multiple reasoning paths and ensemble to improve robustness.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate multiple solutions via Custom with step-by-step prompts
        step_by_step_prompts = [
            "Break down the problem into smaller steps and explain the reasoning behind each step.",
            "Solve this by identifying key entities and tracing connections between them.",
            "First identify what is being asked, then find relevant information in the context, and finally synthesize the answer."
        ]
        
        solutions = []
        for prompt in step_by_step_prompts:
            solution = await self.custom(instruction=prompt)
            solutions.append(solution)

        # Step 3: Ensemble the multiple solutions to get a robust answer
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the ensembled answer for refinement
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer