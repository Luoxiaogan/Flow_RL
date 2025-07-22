# Workflow ID: hotpotqa_118_0
# Benchmark: hotpotqa
# Data Indices: [2964, 589, 1223, 3229, 1549]

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
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate multi-step reasoning using Custom with step-by-step instruction
        step_by_step_reasoning = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom to explore multi-hop reasoning via iterative refinement
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis and refine it through fact-checking and logical connections",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Ensemble all solutions to select the most well-supported one
        solutions = [direct_answer, step_by_step_reasoning, iterative_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to ensure accuracy and coherence
        final_solution = await self.review(pre_solution=final_answer)

        return final_solution