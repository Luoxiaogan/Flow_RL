# Workflow ID: limr_92_0
# Benchmark: limr
# Data Indices: [277, 159]

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

        # Step 1: Initial Analysis and Problem Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify it:
            - Identify the domain (geometry, number theory, combinatorics, etc.)
            - Extract key components (variables, constraints, relationships)
            - Determine the expected answer format (integer, equation, etc.)
            Provide structured output.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        sub_problems = await self.generate(
            instruction=f"""Break the problem into sub-problems:
            Based on the analysis: {initial_analysis}
            - Define independent sub-problems
            - Specify required inputs and outputs for each
            - Highlight dependencies between sub-problems""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration of Solution Paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                Sub-problems: {sub_problems}
                Show all steps and maintain precision.""",
                context=sub_problems
            ),
            self.generate(
                instruction=f"""Solve using geometric methods:
                Sub-problems: {sub_problems}
                Visualize relationships and derive equations.""",
                context=sub_problems
            ),
            self.generate(
                instruction=f"""Solve using combinatorial methods:
                Sub-problems: {sub_problems}
                Count possibilities and apply constraints.""",
                context=sub_problems
            )
        )

        # Step 4: Ensemble to Select or Synthesize Best Solution
        best_solution = await self.ensemble(
            instruction="""Evaluate and synthesize solutions:
            - Compare algebraic, geometric, and combinatorial approaches
            - Select the most complete and accurate solution
            - Combine complementary insights if necessary""",
            contexts_list=solution_paths
        )

        # Step 5: Iterative Refinement
        refined_solution = best_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                Solution: {refined_solution}
                Check for logical consistency, arithmetic accuracy, and adherence to constraints.""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution:
                    Validation feedback: {validation}
                    Correct errors and improve clarity.""",
                    context=refined_solution
                )
            else:
                break

        # Step 6: Final Answer Extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final answer:
            Refined solution: {refined_solution}
            Ensure the answer is an integer between 000 and 999.""",
            context=refined_solution
        )

        return final_answer