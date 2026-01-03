# Workflow ID: gsm8k_122_0
# Benchmark: gsm8k
# Data Indices: [232, 285]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        
        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify all numerical values and their context (e.g., units, relationships).
            - Determine what the question is asking for.
            - Classify the problem type (e.g., sequential, rate, proportion, distribution).
            Provide structured output with clear categories.""",
            context=""
        )
        
        # Step 2: Sub-Problem Decomposition
        sub_problems = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Decompose the problem into smaller, independent sub-problems:
            - Each sub-problem should focus on a specific calculation or relationship.
            - Ensure sub-problems can be solved independently.
            List the sub-problems clearly.""",
            context=initial_analysis
        )
        
        # Step 3: Solve Sub-Problems in Parallel
        sub_problem_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve this sub-problem:
                {sub_problem}
                
                Show all steps and intermediate results explicitly.
                Ensure calculations are precise and units are tracked.""",
                context=sub_problems
            ) for sub_problem in sub_problems.split("\n") if sub_problem.strip()]
        )
        
        # Step 4: Solution Synthesis
        combined_solution = await self.ensemble(
            instruction=f"""Synthesize the solutions to the sub-problems:
            Sub-problem solutions:
            {sub_problem_solutions}
            
            Combine them into a coherent solution to the original problem.
            Ensure consistency and logical flow between steps.""",
            contexts_list=sub_problem_solutions
        )
        
        # Step 5: Iterative Refinement
        refined_solution = combined_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate this solution:
                {refined_solution}
                
                Check for:
                - Correctness of calculations
                - Consistency of units
                - Logical flow between steps
                Highlight any issues.""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution to fix the following issues:
                    {validation}
                    
                    Ensure all corrections are applied and revalidate.""",
                    context=refined_solution
                )
            else:
                break
        
        # Step 6: Final Output
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from the refined solution:
            {refined_solution}
            
            Ensure the answer is a single numerical value (integer or decimal).
            Include no additional text or explanation.""",
            context=refined_solution
        )
        
        return final_answer