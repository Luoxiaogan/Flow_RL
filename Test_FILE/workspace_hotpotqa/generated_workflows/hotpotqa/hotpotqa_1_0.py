# Workflow ID: hotpotqa_1_0
# Benchmark: hotpotqa
# Data Indices: [2049, 212, 3471, 1092]

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
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution and reviews it for final verification.
        """
        # Step 1: Generate multiple solutions using different custom instructions
        solutions = []
        
        # Reasoning path 1: Break down into smaller steps
        sol1 = await self.custom(instruction="Can you break down the problem into smaller steps?")
        solutions.append(sol1)
        
        # Reasoning path 2: Solve by detailed step-by-step reasoning
        sol2 = await self.custom(instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step.")
        solutions.append(sol2)
        
        # Reasoning path 3: Use flexible custom with sequential reasoning pattern
        sol3 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solutions.append(sol3)
        
        # Step 2: Ensemble the best solution from multiple reasoning paths
        ensembled_solution = await self.sc_ensemble(solutions=solutions)
        
        # Step 3: Review the ensembled solution to improve accuracy
        final_answer = await self.review(pre_solution=ensembled_solution)
        
        return final_answer