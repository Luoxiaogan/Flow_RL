# Workflow ID: hotpotqa_689_0
# Benchmark: hotpotqa
# Data Indices: [2370, 2349, 1139, 2072]

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
        # Step 1: Generate initial answer (hypothesis)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use Review to check the initial answer against context
        reviewed_answer = await self.review(pre_solution=initial_answer)
        
        # Step 3: Use FlexibleCustom in iterative mode to refine the answer further
        refined_answer = await self.flexible_custom(
            custom_instruction="Refine the answer by checking each step of reasoning and verifying against the context.",
            previous_results=[reviewed_answer],
            reasoning_pattern="iterative",
            steps=["verify_facts", "trace_connections", "reconstruct_answer"],
            max_iterations=2
        )
        
        # Step 4: Ensemble with original and refined answers for final selection
        ensemble_solution = await self.sc_ensemble(solutions=[initial_answer, reviewed_answer, refined_answer])
        
        return ensemble_solution