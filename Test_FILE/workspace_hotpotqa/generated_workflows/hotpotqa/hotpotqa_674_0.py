# Workflow ID: hotpotqa_674_0
# Benchmark: hotpotqa
# Data Indices: [3988, 400, 1482, 2749, 1816]

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
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple solutions via different reasoning patterns
        solutions = []
        
        # Reasoning path 1: Break down into steps with clear explanation
        solution1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solutions.append(solution1)

        # Reasoning path 2: Use flexible custom with sequential reasoning to trace connections
        solution2 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solutions.append(solution2)

        # Reasoning path 3: Use flexible custom with iterative refinement
        solution3 = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis and refine it through fact-checking",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )
        solutions.append(solution3)

        # Step 2: Ensemble the top solutions
        ensemble_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to improve accuracy
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution