# Workflow ID: hotpotqa_871_0
# Benchmark: hotpotqa
# Data Indices: [3583, 3019, 1153, 913, 1819]

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
        then ensembles the best solution using ScEnsemble, and finally reviews it.
        """
        # Generate multiple solutions using different step-by-step prompts
        solutions = []
        
        # Step 1: Break down the problem into smaller steps
        solution1 = await self.custom(instruction="Can you break down the problem into smaller steps?")
        solutions.append(solution1)
        
        # Step 2: Solve by detailed reasoning with clear explanations
        solution2 = await self.custom(instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step.")
        solutions.append(solution2)
        
        # Step 3: Use flexible custom with sequential reasoning for multi-hop tracing
        solution3 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solutions.append(solution3)
        
        # Ensemble the best solution from multiple reasoning paths
        ensemble_solution = await self.sc_ensemble(solutions=solutions)
        
        # Final review to refine the ensemble result
        final_answer = await self.review(pre_solution=ensemble_solution)
        
        return final_answer