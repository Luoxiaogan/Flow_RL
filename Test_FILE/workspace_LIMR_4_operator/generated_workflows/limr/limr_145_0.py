# Workflow ID: limr_145_0
# Benchmark: limr
# Data Indices: [120, 33]

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

        # Step 1: Analyze and classify the problem
        classification = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            - Geometry: Involves shapes, transformations, or spatial relationships
            - Number Theory: Focuses on integers, divisibility, or modular arithmetic
            - Algebra: Includes equations, polynomials, or functional relationships
            - Combinatorics: Concerns counting, permutations, or probability
            - Optimization: Seeks maxima/minima or extremal values
            Provide a clear classification and explain the reasoning.""",
            context=""
        )

        # Step 2: Decompose the problem into sub-problems
        decomposition = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Break the problem into smaller, manageable sub-problems. Identify:
            - Key variables and constraints
            - Relevant mathematical techniques
            - Potential solution strategies""",
            context=classification
        )

        # Step 3: Explore multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using geometric techniques:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using number-theoretic techniques:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using algebraic techniques:
                {decomposition}""",
                context=decomposition
            )
        )

        # Step 4: Synthesize the best solution
        synthesis = await self.ensemble(
            instruction="""Evaluate the following solution attempts and select the most promising one:
            - Consider correctness, clarity, and completeness
            - Combine insights from multiple approaches if beneficial""",
            contexts_list=strategies
        )

        # Step 5: Iterative refinement and validation
        refined_solution = synthesis
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {refined_solution}
                
                Check for:
                - Logical consistency
                - Computational accuracy
                - Alignment with problem constraints""",
                context=refined_solution
            )
            if "error" in validation.lower() or "incomplete" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    {validation}""",
                    context=refined_solution
                )
            else:
                break

        # Step 6: Summarize the final solution
        final_answer = await self.summarize(
            instruction="""Condense the solution into a concise, final answer:
            - Present the result clearly
            - Include only essential details
            - Ensure the format matches the expected output (integer between 000 and 999)""",
            context=refined_solution
        )

        return final_answer