# Workflow ID: limr_120_0
# Benchmark: limr
# Data Indices: [74, 266]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.llm)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Initial Analysis and Problem Classification
        analysis = await self.generate(
            instruction="""Classify the problem and extract key information:
            - Identify the domain (geometry, number theory, algebra, etc.)
            - List all variables, constants, and relationships
            - Determine constraints and expected answer format (integer 000-999)
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Solution Exploration
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic manipulation:
                - Perform symbolic calculations
                - Simplify expressions
                - Solve for unknowns""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using geometric reasoning:
                - Analyze shapes, angles, and spatial relationships
                - Apply geometric theorems and properties
                - Calculate areas, volumes, or distances""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using combinatorial enumeration:
                - Count possibilities systematically
                - Use permutations, combinations, or probability principles
                - Verify counts match constraints""",
                context=analysis
            )
        )

        # Step 3: Iterative Refinement
        refined_solutions = []
        for solution in solutions:
            refined = await self.revise(
                instruction="""Refine the solution:
                - Verify all calculations
                - Clarify ambiguous steps
                - Address potential errors""",
                context=solution
            )
            refined_solutions.append(refined)

        # Step 4: Synthesis and Final Answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Evaluate logical consistency and precision
            - Resolve conflicts between approaches
            - Select the most robust answer""",
            contexts_list=refined_solutions
        )

        # Step 5: Rigorous Validation
        validation = await self.generate(
            instruction=f"""Validate the final answer:
            - Cross-check intermediate results
            - Test against edge cases
            - Confirm the answer is an integer between 000 and 999""",
            context=final_answer
        )

        if "error" in validation.lower() or "invalid" in validation.lower():
            # Trigger feedback loop for re-evaluation
            return await self.run_workflow()
        else:
            return final_answer