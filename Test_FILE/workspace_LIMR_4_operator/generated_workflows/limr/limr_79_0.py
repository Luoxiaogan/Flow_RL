# Workflow ID: limr_79_0
# Benchmark: limr
# Data Indices: [42, 162]

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

        # Step 1: Initial Analysis - Classify the problem and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the domain (algebra, geometry, combinatorics, etc.)
            - Extract key variables, constraints, and relationships
            - Determine the expected solution format (integer between 000 and 999)
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration - Generate multiple solution approaches
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                - Define equations and unknowns
                - Apply transformations and substitutions
                - Solve step-by-step with full precision""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using geometric reasoning:
                - Visualize spatial relationships
                - Apply trigonometric identities and coordinate geometry
                - Calculate exact values""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using combinatorial techniques:
                - Count possibilities systematically
                - Use generating functions or recursive relations
                - Ensure all cases are covered""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Check each strategy for correctness
        refined_strategies = []
        for strategy in strategies:
            validation = await self.generate(
                instruction=f"""Validate this solution:
                - Check all calculations and logical steps
                - Verify adherence to constraints
                - Highlight any errors or ambiguities""",
                context=strategy
            )
            if "error" in validation.lower():
                refined_strategy = await self.revise(
                    instruction=f"""Revise the solution to fix errors:
                    - Address issues highlighted in validation
                    - Maintain precision and logical consistency""",
                    context=strategy
                )
                refined_strategies.append(refined_strategy)
            else:
                refined_strategies.append(strategy)

        # Step 4: Ensemble Decision - Select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Select the most robust and precise solution:
            - Compare all approaches for correctness and completeness
            - Synthesize complementary insights if necessary
            - Ensure the final answer is an integer between 000 and 999""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Verification - Double-check the chosen solution
        verification = await self.generate(
            instruction=f"""Verify the final solution:
            - Recheck all steps and calculations
            - Confirm adherence to problem constraints
            - Ensure the answer is an integer between 000 and 999""",
            context=final_solution
        )

        # Return the verified final solution
        return verification