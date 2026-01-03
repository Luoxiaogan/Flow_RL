# Workflow ID: limr_135_0
# Benchmark: limr
# Data Indices: [245, 62]

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

        # Phase 1: Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify the domain (geometry, number theory, etc.)
            - Extract key entities (variables, constants, relationships)
            - List constraints and boundary conditions
            - Classify the problem type (exact calculation, estimation, proof, etc.)""",
            context=""
        )
        summary = await self.summarize(
            instruction="Condense the analysis into a structured format.",
            context=analysis
        )

        # Phase 2: Exploration (Parallel Strategies)
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Attempt solution using algebraic methods: {summary}",
                context=""
            ),
            self.generate(
                instruction=f"Attempt solution using combinatorial methods: {summary}",
                context=""
            ),
            self.generate(
                instruction=f"Attempt solution using geometric methods: {summary}",
                context=""
            )
        )
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Improve clarity, add missing details, and verify calculations.",
                context=strategy
            ) for strategy in strategies]
        )

        # Phase 3: Synthesis
        synthesis = await self.ensemble(
            instruction="Evaluate and synthesize the best solution from the refined strategies.",
            contexts_list=refined_strategies
        )

        # Phase 4: Validation
        validation = await self.generate(
            instruction=f"Verify the solution: {synthesis}. Check for logical consistency, computational accuracy, and edge cases.",
            context=""
        )
        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"Fix issues identified in validation: {validation}",
                context=synthesis
            )
            return refined_solution
        else:
            return synthesis