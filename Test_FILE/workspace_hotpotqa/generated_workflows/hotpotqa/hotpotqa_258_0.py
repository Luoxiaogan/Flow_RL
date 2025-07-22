# Workflow ID: hotpotqa_258_0
# Benchmark: hotpotqa
# Data Indices: [2160, 2953, 1929, 379, 3252]

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
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use iterative review to refine the answer
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            revised_answer = await self.review(pre_solution=refined_answer)
            refined_answer = revised_answer
        
        # Step 3: Optional ensemble step — generate multiple solutions and select best
        solution_list = [
            await self.answer_generate(),
            await self.custom(instruction="Break down the problem into smaller steps and explain reasoning"),
            await self.flexible_custom(
                custom_instruction="Use iterative reasoning to trace connections across the context",
                reasoning_pattern="iterative",
                steps=["identify_key_facts", "map_connections", "trace_paths", "synthesize_answer"],
                max_iterations=2
            )
        ]
        
        final_answer = await self.sc_ensemble(solutions=solution_list)
        
        return final_answer