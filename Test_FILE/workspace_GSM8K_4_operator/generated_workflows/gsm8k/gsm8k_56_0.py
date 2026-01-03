# Workflow ID: gsm8k_56_0
# Benchmark: gsm8k
# Data Indices: [164, 77]

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

        # Step 1: Initial Analysis - Extract key information
        initial_analysis = await self.generate(
            instruction="""Analyze the problem to extract:
            - All numerical values and their units
            - Relationships between quantities
            - The target quantity to solve for
            Provide structured output.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition - Break into sub-problems
        sub_problems = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Decompose the problem into smaller sub-problems.
            Each sub-problem should correspond to a single calculation step.
            List all sub-problems with their dependencies.""",
            context=initial_analysis
        )

        # Step 3: Parallel Processing of Independent Sub-Problems
        # Parse sub-problems and identify independent ones
        independent_sub_problems = await self.generate(
            instruction=f"""From the sub-problems:
            {sub_problems}
            
            Identify which sub-problems are independent of each other.
            List these independent sub-problems.""",
            context=sub_problems
        )

        # Process independent sub-problems in parallel
        independent_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve this sub-problem:
                {sub_problem}""",
                context=sub_problems
            ) for sub_problem in independent_sub_problems.split("\n") if sub_problem.strip()]
        )

        # Step 4: Sequential Chaining for Dependent Sub-Problems
        dependent_sub_problems = await self.generate(
            instruction=f"""From the sub-problems:
            {sub_problems}
            
            Identify which sub-problems depend on others.
            List these dependent sub-problems in order of dependency.""",
            context=sub_problems
        )

        cumulative_context = "\n".join(independent_results)
        for sub_problem in dependent_sub_problems.split("\n"):
            if sub_problem.strip():
                result = await self.generate(
                    instruction=f"""Solve this sub-problem using previous results:
                    {sub_problem}""",
                    context=cumulative_context
                )
                cumulative_context += f"\n{result}"

        # Step 5: Validation and Refinement
        validation = await self.revise(
            instruction="""Validate all intermediate results:
            - Check for calculation errors
            - Ensure units are consistent
            - Verify logical consistency""",
            context=cumulative_context
        )

        if "error" in validation.lower():
            refined_results = await self.revise(
                instruction=f"""Correct the following issues:
                {validation}""",
                context=cumulative_context
            )
            cumulative_context = refined_results

        # Step 6: Final Synthesis
        final_answer = await self.ensemble(
            instruction="""Synthesize all intermediate results to compute the final answer.
            Ensure the answer is numerically exact and includes appropriate units.""",
            contexts_list=[cumulative_context]
        )

        return final_answer