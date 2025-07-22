# Workflow ID: hotpotqa_429_0
# Benchmark: hotpotqa
# Data Indices: [422, 3469, 3876, 2789, 1741]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It first breaks down the problem, then uses flexible custom to trace connections step-by-step.
        Finally, it reviews and ensembles solutions to improve accuracy.
        """
        # Step 1: Break down the problem into smaller steps for better understanding
        breakdown = await self.custom(instruction="Can you break down the problem into smaller steps?")
        
        # Step 2: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )
        
        # Step 3: Review the generated solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)
        
        # Step 4: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()
        
        # Step 5: Ensemble the original and reviewed solutions for robustness
        final_solution = await self.sc_ensemble(solutions=[solution, reviewed_solution, direct_answer])
        
        return final_solution