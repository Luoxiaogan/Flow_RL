# Workflow ID: hotpotqa_326_0
# Benchmark: hotpotqa
# Data Indices: [2054, 374, 1301, 2210, 3618]

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
        It generates multiple reasoning paths using different Custom instructions,
        then ensembles the best solution, and finally reviews it for correctness.
        """
        # Step 1: Generate diverse reasoning paths using different custom instructions
        solutions = []
        
        # Reasoning path 1: Break down the problem step by step
        solution1 = await self.custom(instruction="Can you break down the problem into smaller steps?")
        solutions.append(solution1)
        
        # Reasoning path 2: Solve by identifying key entities and connections
        solution2 = await self.custom(instruction="Identify the key entities in the problem and trace how they connect to form the answer.")
        solutions.append(solution2)
        
        # Reasoning path 3: Use iterative refinement to improve the answer
        solution3 = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis and refine it based on logical connections.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_connections", "refine_answer"],
            max_iterations=2
        )
        solutions.append(solution3)
        
        # Step 2: Ensemble the best solution from the diverse paths
        ensemble_solution = await self.sc_ensemble(solutions=solutions)
        
        # Step 3: Final review to ensure correctness and completeness
        final_answer = await self.review(pre_solution=ensemble_solution)
        
        return final_answer