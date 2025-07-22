# Workflow ID: hotpotqa_649_0
# Benchmark: hotpotqa
# Data Indices: [971, 168, 3746, 2625, 2696]

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
        This is a workflow graph for multi-hop question answering with iterative refinement.
        Starts with an initial answer, then iteratively refines it using review and flexible custom reasoning.
        """
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use Review to refine the initial answer based on context
        refined_answer = await self.review(pre_solution=initial_answer)
        
        # Step 3: Use FlexibleCustom in iterative mode to progressively refine the answer
        # This allows multi-hop reasoning by breaking down the problem step-by-step
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each one carefully.",
            reasoning_pattern="iterative",
            steps=["identify_key_entities", "trace_intermediate_connections", "verify_facts", "synthesize_final_answer"],
            max_iterations=3
        )
        
        # Step 4: Ensemble the refined answer with the iterative result for robustness
        final_solution = await self.sc_ensemble(solutions=[refined_answer, iterative_refinement])
        
        return final_solution