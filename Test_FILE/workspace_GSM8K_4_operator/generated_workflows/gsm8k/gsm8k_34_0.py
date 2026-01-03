# Workflow ID: gsm8k_34_0
# Benchmark: gsm8k
# Data Indices: [145, 249]

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
            - Extract all numerical values and their units
            - Identify relationships and constraints
            - Classify the problem type (e.g., sequential, rate, distribution)
            - Outline potential solution strategies""",
            context=""
        )

        # Step 2: Parallel Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction="""Solve using direct calculations:
                - Perform step-by-step arithmetic
                - Track intermediate results explicitly""",
                context=initial_analysis
            ),
            self.generate(
                instruction="""Solve using proportional reasoning:
                - Identify ratios, percentages, or fractions
                - Scale values accordingly""",
                context=initial_analysis
            ),
            self.generate(
                instruction="""Solve using unit conversions:
                - Convert units as needed
                - Ensure consistency across calculations""",
                context=initial_analysis
            )
        )

        # Step 3: Strategy Selection
        selected_strategy = await self.ensemble(
            instruction="""Select the most promising strategy:
            - Evaluate clarity and completeness
            - Check alignment with problem requirements
            - Prioritize strategies with explicit intermediate steps""",
            contexts_list=strategies
        )

        # Step 4: Iterative Execution
        steps = selected_strategy.split("\n")
        result = ""
        for i, step in enumerate(steps):
            computation = await self.generate(
                instruction=f"""Execute step {i+1}:
                - Perform the calculation described in: {step}
                - Document intermediate results""",
                context=result
            )
            validation = await self.revise(
                instruction=f"""Validate step {i+1}:
                - Check for calculation errors
                - Ensure logical consistency
                - Revise if necessary""",
                context=computation
            )
            result += f"{validation}\n"

        # Step 5: Final Synthesis
        final_answer = await self.summarize(
            instruction="""Condense the solution into a single numerical answer:
            - Include only the final result
            - Ensure the format matches the problem requirements""",
            context=result
        )

        return final_answer.strip()