# Workflow ID: hotpotqa_115_0
# Benchmark: hotpotqa
# Data Indices: [3379, 3443, 1650, 3732]

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
        # Generate multiple solutions using different step-by-step instructions
        solutions = []
        
        # First path: Break down into smaller steps with clear reasoning
        solution1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solutions.append(solution1)

        # Second path: Use flexible custom with sequential reasoning for structured multi-hop logic
        solution2 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solutions.append(solution2)

        # Third path: Use iterative refinement to improve initial answer
        solution3 = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis then verify against context",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )
        solutions.append(solution3)

        # Ensemble the top solutions to select the most well-supported answer
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Final review to ensure coherence and correctness
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution