# Workflow ID: gsm8k_121_0
# Benchmark: gsm8k
# Data Indices: [43, 78]

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
        import re
        
        # Step 1: Initial Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Extract all numerical values and their units
            - Identify relationships between quantities
            - Classify the problem type (e.g., rate, proportion, distribution)
            - List constraints and conditions explicitly
            Provide a structured summary.""",
            context=""
        )
        
        # Step 2: Dynamic Instruction Construction
        instructions = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Construct detailed instructions for solving the problem:
            - Specify the sequence of calculations
            - Highlight intermediate results to track
            - Define the expected format of the final answer""",
            context=analysis
        )
        
        # Step 3: Parallel Exploration of Solution Paths
        exact_solution = self.generate(
            instruction=f"""Solve using precise calculations:
            Instructions: {instructions}
            Show all steps and intermediate results.""",
            context=instructions
        )
        estimation_solution = self.generate(
            instruction=f"""Solve using estimation techniques:
            Instructions: {instructions}
            Focus on approximate values and reasonable assumptions.""",
            context=instructions
        )
        solutions = await asyncio.gather(exact_solution, estimation_solution)
        
        # Step 4: Synthesize Optimal Solution
        synthesis = await self.ensemble(
            instruction="""Compare the two solutions:
            - Evaluate accuracy and precision
            - Check consistency with problem constraints
            - Select the most reliable and efficient solution""",
            contexts_list=solutions
        )
        
        # Step 5: Iterative Refinement
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction=f"""Validate the solution:
                Solution: {synthesis}
                Check for calculation errors, logical gaps, or missing details.""",
                context=synthesis
            )
            if "error" in validation.lower():
                synthesis = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    Feedback: {validation}
                    Correct errors and improve clarity.""",
                    context=synthesis
                )
            else:
                break
        
        # Step 6: Final Answer Extraction
        final_answer = await self.summarize(
            instruction=f"""Extract the final numerical answer:
            Solution: {synthesis}
            Ensure the answer is a single numerical value.""",
            context=synthesis
        )
        
        # Clean and return the final answer
        match = re.search(r'\d+(\.\d+)?', final_answer)
        return float(match.group()) if match else None