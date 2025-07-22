# Workflow ID: hotpotqa_515_0
# Benchmark: hotpotqa
# Data Indices: [2619, 2534, 3677, 1467, 3402]

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
        This is a workflow graph for multi-hop question answering using iterative refinement.
        Starts with an initial answer, then iteratively reviews and refines it based on context.
        """
        # Step 1: Generate initial answer (direct reasoning)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom with iterative pattern to refine the answer
        refined_answer = await self.flexible_custom(
            custom_instruction="Refine the answer by checking facts step-by-step and correcting errors",
            reasoning_pattern="iterative",
            steps=["verify_facts", "check_consistency", "correct_errors"],
            max_iterations=3
        )
        
        # Step 3: Final review to ensure correctness
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer