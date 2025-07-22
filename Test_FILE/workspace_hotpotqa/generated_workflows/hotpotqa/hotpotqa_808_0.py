# Workflow ID: hotpotqa_808_0
# Benchmark: hotpotqa
# Data Indices: [358, 2990, 1305, 1220, 1711]

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
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()
        
        # Step 2: Use Review to iteratively refine the answer based on context
        refined_answer = await self.review(pre_solution=initial_answer)
        
        # Step 3: Use FlexibleCustom with iterative pattern to further refine through structured reasoning steps
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and verify each step against the context.",
            reasoning_pattern="iterative",
            steps=["identify_key_facts", "trace_logical_connections", "verify_evidence", "synthesize_final_answer"],
            max_iterations=2
        )
        
        # Step 4: Ensemble the refined answer with the iterative result to ensure robustness
        solutions = [refined_answer, iterative_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer