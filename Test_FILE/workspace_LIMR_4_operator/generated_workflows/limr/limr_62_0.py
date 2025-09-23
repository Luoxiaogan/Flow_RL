# Workflow ID: limr_62_0
# Benchmark: limr
# Data Indices: [101, 184]

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

        # Phase 1: Problem Analysis and Decomposition
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key components (e.g., variables, constraints, relationships)
            - Classify the problem type (geometry, algebra, combinatorics, etc.)
            - Highlight any special conditions or requirements
            Provide a structured breakdown.""",
            context=""
        )
        summary = await self.summarize(
            instruction="Condense the analysis into a concise summary of key points.",
            context=analysis
        )

        # Phase 2: Parallel Exploration of Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                - Perform symbolic manipulations
                - Solve equations or inequalities
                - Verify intermediate steps""",
                context=summary
            ),
            self.generate(
                instruction=f"""Solve using geometric reasoning:
                - Visualize the problem
                - Apply geometric theorems or coordinate transformations
                - Check consistency with given constraints""",
                context=summary
            ),
            self.generate(
                instruction=f"""Solve using combinatorial techniques:
                - Enumerate cases or possibilities
                - Apply counting principles
                - Validate against constraints""",
                context=summary
            )
        )
        synthesis = await self.ensemble(
            instruction="Synthesize the results from all paths into a unified solution.",
            contexts_list=paths
        )

        # Phase 3: Iterative Refinement and Validation
        refined = synthesis
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the solution for correctness, clarity, and precision.",
                context=refined
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Address issues identified in validation: {validation}",
                    context=refined
                )
            else:
                break

        return refined