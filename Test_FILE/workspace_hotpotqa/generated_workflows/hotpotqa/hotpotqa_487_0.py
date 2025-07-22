# Workflow ID: hotpotqa_487_0
# Benchmark: hotpotqa
# Data Indices: [881, 3090, 3147, 1714, 1877]

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
        # Generate multiple solutions using different custom instructions
        solutions = []
        
        # Step 1: Use flexible custom with sequential reasoning for structured multi-hop steps
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, step-by-step reasoning paths.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )
        solutions.append(seq_solution)

        # Step 2: Use flexible custom with iterative refinement to improve answer quality
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an initial answer, then verify and refine it based on context.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )
        solutions.append(iter_solution)

        # Step 3: Use standard Custom with detailed step-by-step breakdown
        custom_solution = await self.custom(
            instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"
        )
        solutions.append(custom_solution)

        # Step 4: Ensemble the top solutions
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to catch any remaining errors or inconsistencies
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer