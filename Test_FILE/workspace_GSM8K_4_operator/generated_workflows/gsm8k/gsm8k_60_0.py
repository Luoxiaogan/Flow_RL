# Workflow ID: gsm8k_60_0
# Benchmark: gsm8k
# Data Indices: [248, 180]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract all numerical values and their context.
            - Identify explicit and implicit constraints.
            - Classify the problem type (sequential, rate, distribution, etc.).
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Solution Strategy
        strategy = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Develop a solution strategy:
            - For sequential problems, outline step-by-step calculations.
            - For rate problems, focus on relationships between variables.
            - For distribution problems, track quantities and remainders.
            Provide a detailed plan.""",
            context=analysis
        )

        # Step 3: Parallel Solution Attempts
        attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using precise calculations:
                {strategy}""",
                context=strategy
            ),
            self.generate(
                instruction=f"""Solve emphasizing unit consistency:
                {strategy}""",
                context=strategy
            ),
            self.generate(
                instruction=f"""Solve exploring alternative interpretations:
                {strategy}""",
                context=strategy
            )
        )

        # Step 4: Validation and Refinement
        refined_attempts = []
        for attempt in attempts:
            validation = await self.generate(
                instruction=f"""Validate this solution:
                {attempt}
                
                Check intermediate results, numerical precision, and final answer format.
                Highlight any issues.""",
                context=attempt
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Fix issues identified in validation:
                    {validation}""",
                    context=attempt
                )
                refined_attempts.append(refined)
            else:
                refined_attempts.append(attempt)

        # Step 5: Ensemble Decision
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Numerical correctness.
            - Clarity of reasoning.
            - Alignment with problem constraints.""",
            contexts_list=refined_attempts
        )

        return final_solution