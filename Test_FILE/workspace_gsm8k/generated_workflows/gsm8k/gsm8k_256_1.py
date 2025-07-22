# Workflow ID: gsm8k_256_1
# Benchmark: gsm8k
# Data Indices: [237, 402]

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
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Diverse and effective workflow combining Iterative Refinement + Reflect-and-Regenerate.
        1. Use FlexibleCustom with iterative reasoning pattern to generate an initial solution through structured steps.
        2. Review the result to improve clarity and correctness.
        3. Reflect on the revised solution to uncover potential oversights or alternative interpretations.
        4. Based on reflection, regenerate a final answer using Custom with targeted instruction.
        
        This workflow introduces a meta-cognitive loop (reflect → regenerate) after an iterative refinement phase, creating deeper reasoning than simple step-by-step or ensemble methods.
        """

        # Step 1: Use iterative FlexibleCustom for systematic exploration
        iterative_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Approach the problem systematically by breaking it into smaller subproblems."
        )

        # Step 2: Improve the solution via review
        refined_solution = await self.review(pre_solution=iterative_solution)

        # Step 3: Critically reflect on the refined solution without rewriting
        reflection = await self.reflect(pre_solution=refined_solution)

        # Step 4: Use reflection to guide a new, improved solution generation
        final_answer = await self.custom(
            instruction=f"Given the following reflection about the current solution:\n\n{reflection}\n\nNow, provide a final, comprehensive answer that addresses any overlooked aspects, assumptions, or edge cases. Be precise and thorough."
        )

        return final_answer