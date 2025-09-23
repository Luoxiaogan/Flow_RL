# Workflow ID: limr_126_0
# Benchmark: limr
# Data Indices: [260, 127]

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
            - Classify the problem type (geometry, number theory, etc.)
            - Extract key entities, numbers, and relationships
            - Identify constraints and conditions
            Format the output as a structured summary.""",
            context=""
        )

        # Step 2: Parallel Solution Attempts
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                - Translate the problem into equations
                - Solve step-by-step with precise calculations
                - Verify intermediate results""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using geometric methods:
                - Represent the problem visually if applicable
                - Use coordinate geometry or trigonometric identities
                - Ensure all transformations are valid""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using combinatorial methods:
                - Apply counting principles and probability rules
                - Enumerate cases systematically
                - Check for overcounting or undercounting""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Revision
        validated_solutions = []
        for attempt in solution_attempts:
            validation = await self.revise(
                instruction="""Validate the solution:
                - Check for logical consistency
                - Verify all calculations
                - Ensure adherence to constraints""",
                context=attempt
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Revise the solution to fix issues:
                    - Address errors identified in validation
                    - Recompute affected steps""",
                    context=validation
                )
                validated_solutions.append(refined)
            else:
                validated_solutions.append(validation)

        # Step 4: Synthesis and Selection
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Compare accuracy and efficiency
            - Ensure the answer is an integer between 000 and 999
            - Resolve any discrepancies""",
            contexts_list=validated_solutions
        )

        # Step 5: Final Verification
        verified_solution = await self.revise(
            instruction="""Perform final verification:
            - Double-check all steps
            - Confirm the answer format
            - Ensure no constraints are violated""",
            context=final_solution
        )

        return verified_solution