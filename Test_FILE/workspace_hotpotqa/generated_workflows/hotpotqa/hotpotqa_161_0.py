# Workflow ID: hotpotqa_161_0
# Benchmark: hotpotqa
# Data Indices: [948, 2300, 1826, 3208]

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
        It generates multiple reasoning paths using Custom operators with step-by-step instructions,
        then ensembles the best solution using ScEnsemble, and finally reviews the selected answer.
        """
        # Step 1: Generate multiple reasoning paths using different custom instructions
        solutions = []
        
        # Reasoning path 1: Break down into smaller steps
        sol1 = await self.custom(instruction="Can you break down the problem into smaller steps?")
        solutions.append(sol1)

        # Reasoning path 2: Solve by detailed step-by-step reasoning
        sol2 = await self.custom(instruction="Solve this by breaking it down into detailed steps and explaining the reasoning behind each step.")
        solutions.append(sol2)

        # Reasoning path 3: Use structured reasoning to trace connections
        sol3 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solutions.append(sol3)

        # Step 2: Ensemble the solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensemble solution for final verification
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer