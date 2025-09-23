# Workflow ID: limr_89_0
# Benchmark: limr
# Data Indices: [75, 258]

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
            instruction="""Analyze the problem thoroughly:
            - Identify the domain (geometry, number theory, etc.)
            - Extract all given data and constraints
            - Determine the expected answer format
            - Highlight any ambiguities or missing information""",
            context=""
        )

        # Step 2: Parallel Solution Attempts
        algebraic_attempt = self.generate(
            instruction=f"""Solve using algebraic methods:
            - Use equations and symbolic manipulation
            - Show all intermediate steps
            - Validate calculations""",
            context=initial_analysis
        )
        geometric_attempt = self.generate(
            instruction=f"""Solve using geometric methods:
            - Visualize the problem if applicable
            - Use properties of shapes and spatial relationships
            - Validate geometric reasoning""",
            context=initial_analysis
        )
        combinatorial_attempt = self.generate(
            instruction=f"""Solve using combinatorial methods:
            - Count possibilities systematically
            - Use permutations, combinations, or probability principles
            - Validate counting logic""",
            context=initial_analysis
        )
        attempts = await asyncio.gather(algebraic_attempt, geometric_attempt, combinatorial_attempt)

        # Step 3: Validation and Revision
        validated_attempts = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and improve this solution:
                - Check for logical consistency
                - Verify all calculations
                - Add missing details or clarify ambiguous steps""",
                context=attempt
            ) for attempt in attempts]
        )

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Select the most rigorous and complete approach
            - Combine insights from multiple attempts if necessary
            - Ensure the solution satisfies all constraints""",
            contexts_list=validated_attempts
        )

        # Step 5: Final Verification
        verified_solution = await self.revise(
            instruction="""Verify the final solution:
            - Cross-check against the original problem
            - Ensure all constraints are satisfied
            - Confirm the answer matches the expected format""",
            context=final_solution
        )

        return verified_solution