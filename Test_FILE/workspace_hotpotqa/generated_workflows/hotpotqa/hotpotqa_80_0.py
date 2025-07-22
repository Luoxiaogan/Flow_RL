# Workflow ID: hotpotqa_80_0
# Benchmark: hotpotqa
# Data Indices: [1184, 247, 2811, 927]

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
        # Generate multiple solutions using different step-by-step instructions
        solutions = []
        
        # First path: break down into smaller steps with clear reasoning
        sol1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solutions.append(sol1)

        # Second path: use flexible custom with sequential reasoning to trace connections
        sol2 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solutions.append(sol2)

        # Third path: generate an initial answer directly
        sol3 = await self.answer_generate()
        solutions.append(sol3)

        # Ensemble the top solution from the three paths
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Final review to refine the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer