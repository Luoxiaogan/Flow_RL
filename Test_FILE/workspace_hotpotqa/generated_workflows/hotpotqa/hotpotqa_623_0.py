# Workflow ID: hotpotqa_623_0
# Benchmark: hotpotqa
# Data Indices: [1065, 3584, 3007, 491]

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
        # Generate multiple solutions using different custom instructions to encourage step-by-step thinking
        solutions = []
        
        # Path 1: Break down the problem into smaller steps
        sol1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solutions.append(sol1)

        # Path 2: Reason through the problem with clear step-by-step logic
        sol2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step.")
        solutions.append(sol2)

        # Path 3: Use flexible custom with sequential reasoning pattern for structured multi-hop logic
        sol3 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solutions.append(sol3)

        # Ensemble the solutions to select the most well-supported answer
        ensemble_solution = await self.sc_ensemble(solutions=solutions)

        # Final review to verify and refine the selected solution
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer