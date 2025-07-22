# Workflow ID: hotpotqa_32_0
# Benchmark: hotpotqa
# Data Indices: [1790, 3472, 468, 2480, 2331]

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
        # Step 1: Generate multiple solutions using different custom instructions
        solutions = []
        
        # Reasoning path 1: Break down into smaller steps
        sol1 = await self.custom(instruction="Can you break down the problem into smaller steps?")
        solutions.append(sol1)
        
        # Reasoning path 2: Solve with detailed reasoning per step
        sol2 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solutions.append(sol2)
        
        # Reasoning path 3: Focus on connecting information across different parts of the context
        sol3 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["extract_facts", "identify_bridges", "connect_information", "derive_answer"]
        )
        solutions.append(sol3)
        
        # Step 2: Ensemble the solutions to select the best one
        ensembled_solution = await self.sc_ensemble(solutions=solutions)
        
        # Step 3: Review the ensembled solution for final verification
        final_answer = await self.review(pre_solution=ensembled_solution)
        
        return final_answer