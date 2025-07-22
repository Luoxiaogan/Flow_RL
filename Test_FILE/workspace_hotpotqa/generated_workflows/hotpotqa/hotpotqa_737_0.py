# Workflow ID: hotpotqa_737_0
# Benchmark: hotpotqa
# Data Indices: [1116, 1427, 3887, 476]

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
        
        # Step 1: Use flexible custom with sequential reasoning to trace multi-hop connections
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and their relationships.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solutions.append(seq_solution)

        # Step 2: Use flexible custom with iterative refinement for fact-checking
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an initial answer, then verify facts and refine based on context.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )
        solutions.append(iter_solution)

        # Step 3: Use standard Custom to generate a structured reasoning-based answer
        custom_solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solutions.append(custom_solution)

        # Step 4: Ensemble the top solutions to select the most well-supported one
        ensemble_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to ensure correctness and clarity
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer