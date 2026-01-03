# Workflow ID: gsm8k_98_0
# Benchmark: gsm8k
# Data Indices: [45, 115]

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

        # Step 1: Extract key information
        extraction = await self.generate(
            instruction="""Extract all numerical values, units, and relationships:
            - Identify numbers and their context (e.g., 50 pants, 4 pairs annually)
            - Highlight relationships (e.g., receives 4 pairs annually)
            - Determine what the question is asking for""",
            context=""
        )

        # Step 2: Generate multiple solution paths in parallel
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct calculations:
                {extraction}
                - Perform step-by-step arithmetic operations
                - Track intermediate results and units""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Solve using proportional reasoning:
                {extraction}
                - Identify proportional relationships
                - Scale values accordingly""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Solve by breaking into sub-problems:
                {extraction}
                - Divide the problem into smaller parts
                - Solve each part independently""",
                context=extraction
            )
        )

        # Step 3: Select the best path using ensemble
        best_path = await self.ensemble(
            instruction="Select the most accurate and complete solution path",
            contexts_list=paths
        )

        # Step 4: Iterative refinement
        refined_solution = best_path
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {refined_solution}
                - Check for calculation errors
                - Ensure units and relationships are consistent
                - Verify intermediate results""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Fix issues identified during validation:
                    {validation}
                    - Correct errors
                    - Clarify ambiguities""",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Extract final numerical answer
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer:
            {refined_solution}
            - Provide only the numerical value
            - Ensure it matches the question's requirements""",
            context=refined_solution
        )

        return final_answer.strip()