# Workflow ID: limr_125_0
# Benchmark: limr
# Data Indices: [32, 66]

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

        # Step 1: Initial Analysis - Decompose the problem and identify key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the domain (geometry, number theory, etc.)
            - Extract key variables, constraints, and relationships
            - Classify the problem type (exact calculation, estimation, proof, etc.)
            - Define potential solution strategies""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution attempts
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Solve using algebraic methods:
                - Perform symbolic manipulations
                - Verify intermediate steps
                - Present final answer""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Solve using combinatorial reasoning:
                - Enumerate cases systematically
                - Apply counting principles
                - Validate logical consistency""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Solve using geometric techniques:
                - Analyze shapes and spatial relationships
                - Apply trigonometric identities
                - Check dimensional consistency""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Critique and improve each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and refine the following solution:
                - Check for logical errors
                - Verify calculations
                - Enhance clarity and rigor""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 4: Synthesis - Combine insights from parallel branches
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Evaluate trade-offs between approaches
            - Resolve conflicts or inconsistencies
            - Ensure coherence and correctness
            - Present the final answer as an integer between 000 and 999""",
            contexts_list=refined_solutions
        )

        return final_solution