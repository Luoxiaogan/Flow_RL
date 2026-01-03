# Workflow ID: limr_41_0
# Benchmark: limr
# Data Indices: [207, 182]

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
            instruction="""Analyze the problem:
            - Identify the domain (geometry, number theory, combinatorics, etc.)
            - Extract key variables, constraints, and relationships
            - Outline potential solution strategies
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration
        approaches = ["algebraic", "combinatorial", "geometric", "number_theoretic"]
        parallel_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the problem using {approach} reasoning:
                - Show all steps explicitly
                - Maintain precision and rigor
                - Highlight assumptions and constraints""",
                context=initial_analysis
            ) for approach in approaches]
        )

        # Step 3: Validation and Refinement
        validated_attempts = []
        for attempt in parallel_attempts:
            validation = await self.generate(
                instruction=f"""Validate this solution:
                - Check for logical consistency
                - Verify calculations and constraints
                - Identify gaps or errors""",
                context=attempt
            )
            if "error" not in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine this solution:
                    - Improve clarity and structure
                    - Add missing details
                    - Ensure adherence to problem requirements""",
                    context=attempt
                )
                validated_attempts.append(refined)

        # Step 4: Synthesis and Selection
        if validated_attempts:
            final_solution = await self.ensemble(
                instruction="""Select the best solution:
                - Compare based on correctness, clarity, and completeness
                - Ensure the answer is an integer between 000 and 999""",
                contexts_list=validated_attempts
            )
        else:
            final_solution = "No valid solution found."

        # Step 5: Final Verification
        verification = await self.generate(
            instruction=f"""Verify the final solution:
            - Double-check all steps and calculations
            - Confirm adherence to problem constraints
            - Present the final answer in the required format""",
            context=final_solution
        )

        return verification