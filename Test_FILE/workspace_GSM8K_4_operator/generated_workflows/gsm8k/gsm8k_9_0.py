# Workflow ID: gsm8k_9_0
# Benchmark: gsm8k
# Data Indices: [155, 178]

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

        # Initial Problem Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract all numerical values and their context
            - Identify what the question asks for
            - Classify the problem type (sequential, rate, distribution, proportions, multi-entity)
            - Outline potential solution steps""",
            context=""
        )

        # Parallel Solution Approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"Develop a sequential step-by-step solution based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a rate-based solution if applicable based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a distribution-based solution if applicable based on: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Validate and Refine Each Approach
        refined_approaches = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine the solution: {approach}",
                context=approach
            ) for approach in approaches]
        )

        # Summarize Key Insights from Each Refined Approach
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction=f"Summarize key insights from: {refined}",
                context=refined
            ) for refined in refined_approaches]
        )

        # Ensemble to Select Best Solution
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution based on summaries",
            contexts_list=summaries
        )

        # Final Validation and Adjustment
        validated_solution = await self.revise(
            instruction="Perform final validation and adjust if necessary",
            context=final_solution
        )

        # Extract Final Numerical Answer
        final_answer = await self.generate(
            instruction="Extract the final numerical answer from the validated solution",
            context=validated_solution
        )

        return final_answer