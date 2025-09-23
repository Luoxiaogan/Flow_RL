# Workflow ID: limr_34_0
# Benchmark: limr
# Data Indices: [7, 224]

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

        # Step 1: Initial Analysis - Classify problem and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify the mathematical domain (geometry, number theory, etc.)
            - Extract key variables, constants, and relationships
            - Highlight any constraints or special conditions
            - Suggest possible solution strategies""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution attempts
        parallel_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Using an algebraic approach:
                - Solve step-by-step
                - Show all calculations
                - Validate intermediate results""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using a geometric approach:
                - Visualize the problem if applicable
                - Apply coordinate transformations or trigonometric identities
                - Verify geometric properties""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using a combinatorial approach:
                - Count possibilities systematically
                - Apply permutations or combinations
                - Check for overcounting or undercounting""",
                context=initial_analysis
            )
        )

        # Step 3: Iterative Refinement - Critique and improve each solution
        refined_solutions = []
        for solution in parallel_solutions:
            refined = await self.revise(
                instruction="""Critique and refine the solution:
                - Identify and correct errors
                - Improve clarity and precision
                - Add missing steps or justifications""",
                context=solution
            )
            refined_solutions.append(refined)

        # Step 4: Ensemble Synthesis - Combine the best aspects of parallel solutions
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Compare approaches for correctness and efficiency
            - Merge complementary insights
            - Ensure the final answer meets precision requirements""",
            contexts_list=refined_solutions
        )

        # Step 5: Final Validation - Ensure the solution is complete and precise
        validated_solution = await self.revise(
            instruction="""Perform final validation:
            - Double-check all calculations
            - Confirm the answer format (integer between 000 and 999)
            - Ensure all constraints are satisfied""",
            context=final_solution
        )

        return validated_solution