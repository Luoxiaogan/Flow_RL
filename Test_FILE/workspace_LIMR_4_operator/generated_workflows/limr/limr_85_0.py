# Workflow ID: limr_85_0
# Benchmark: limr
# Data Indices: [123, 279]

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
        analysis = await self.generate(
            instruction="""Analyze the problem to identify:
            - Problem type (geometry, number theory, combinatorics, etc.)
            - Key components (variables, constraints, relationships)
            - Expected solution format
            Provide structured output.""",
            context=""
        )

        # Step 2: Generate Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop algebraic solution based on: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Develop geometric solution based on: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Develop combinatorial solution based on: {analysis}",
                context=analysis
            )
        )

        # Step 3: Validate and Refine Strategies
        refined_strategies = []
        for strategy in strategies:
            validated = await self.revise(
                instruction="Validate logical consistency and mathematical rigor.",
                context=strategy
            )
            refined = await self.revise(
                instruction="Refine and clarify the solution approach.",
                context=validated
            )
            refined_strategies.append(refined)

        # Step 4: Iterative Refinement
        final_strategies = []
        for strategy in refined_strategies:
            for _ in range(3):  # Allow up to 3 refinement iterations
                validation = await self.revise(
                    instruction="Check for errors and improve clarity.",
                    context=strategy
                )
                if "error" not in validation.lower():
                    final_strategies.append(validation)
                    break
                strategy = await self.revise(
                    instruction="Fix identified issues.",
                    context=validation
                )

        # Step 5: Final Synthesis
        final_answer = await self.ensemble(
            instruction="Select or synthesize the best solution from validated strategies.",
            contexts_list=final_strategies
        )

        # Step 6: Format Output
        formatted_answer = await self.generate(
            instruction="Format the final answer as an integer between 000 and 999.",
            context=final_answer
        )

        return formatted_answer