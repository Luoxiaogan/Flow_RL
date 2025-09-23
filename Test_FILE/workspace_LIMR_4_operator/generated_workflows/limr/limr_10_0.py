# Workflow ID: limr_10_0
# Benchmark: limr
# Data Indices: [108, 278]

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

        # Step 1: Initial Analysis and Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify its type:
            - Is it algebraic, geometric, combinatorial, or probabilistic?
            - Identify key variables, constraints, and relationships.
            - Highlight any special cases or edge conditions.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis:
                {initial_analysis}
                
                Solve the problem using algebraic techniques:
                - Symbolic manipulation
                - Polynomial factorization
                - Functional equations""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis:
                {initial_analysis}
                
                Solve the problem using geometric techniques:
                - Coordinate geometry
                - Vector calculations
                - Trigonometric identities""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis:
                {initial_analysis}
                
                Solve the problem using combinatorial techniques:
                - Counting principles
                - Recursive reasoning
                - Generating functions""",
                context=initial_analysis
            )
        )

        # Step 3: Iterative Refinement and Validation
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine this solution. Ensure logical consistency and correctness.",
                context=solution
            ) for solution in strategies]
        )

        # Step 4: Synthesis and Final Selection
        final_solution = await self.ensemble(
            instruction="Compare and synthesize the refined solutions. Select the most robust and accurate approach.",
            contexts_list=refined_solutions
        )

        # Step 5: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="Extract the final answer in the required format (integer between 000 and 999). Verify its correctness.",
            context=final_solution
        )

        return final_answer