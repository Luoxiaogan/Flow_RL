# Workflow ID: hotpotqa_266_0
# Benchmark: hotpotqa
# Data Indices: [565, 3842, 3424, 2405, 3146]

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
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to trace multi-hop logic
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and reason through each step carefully.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement to improve answer
        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis and refine it by verifying facts step-by-step.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Use Custom with detailed step-by-step instruction
        detailed_step_solution = await self.custom(
            instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 5: Ensemble all solutions to select the most consistent one
        solutions = [direct_answer, sequential_solution, iterative_solution, detailed_step_solution]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review of the ensembled answer
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer