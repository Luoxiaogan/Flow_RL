# Workflow ID: limr_104_0
# Benchmark: limr
# Data Indices: [27, 69]

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

        # Step 1: Classify the problem domain and identify constraints
        classification = await self.generate(
            instruction="""Analyze the problem to determine:
            - The primary domain (geometry, number theory, etc.)
            - Key constraints and relationships
            - Expected answer format (integer, fraction, etc.)
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Generate multiple solution paths in parallel
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic reasoning:
                - Define variables and equations
                - Solve step-by-step
                - Validate intermediate results""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve using geometric reasoning:
                - Identify shapes and spatial relationships
                - Apply relevant theorems and formulas
                - Validate calculations""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve using combinatorial reasoning:
                - Count possible outcomes
                - Apply probability principles
                - Validate logical consistency""",
                context=classification
            )
        )

        # Step 3: Validate and refine each path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and improve this solution:
                - Check for errors in reasoning or calculation
                - Add missing steps or justifications
                - Ensure alignment with problem constraints""",
                context=path
            ) for path in paths]
        )

        # Step 4: Synthesize results into a unified solution
        final_solution = await self.ensemble(
            instruction="""Select the most complete and accurate solution:
            - Evaluate correctness and completeness
            - Combine complementary insights
            - Present final answer in required format""",
            contexts_list=refined_paths
        )

        return final_solution