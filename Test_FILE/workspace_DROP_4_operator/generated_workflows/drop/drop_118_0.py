# Workflow ID: drop_118_0
# Benchmark: drop
# Data Indices: [495, 66]

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
        import re

        # Step 1: Initial Analysis - Extract entities and classify problem
        initial_analysis = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage. 
            Then classify the problem type:
            - Numerical (counting, arithmetic)
            - Comparison (greater/less than, ranking)
            - Span Extraction (exact text spans)
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution attempts
        arithmetic_attempt = self.generate(
            instruction=f"""Attempt to solve using arithmetic operations:
            - Identify relevant numbers from: {initial_analysis}
            - Perform addition, subtraction, or comparison as needed
            - Show all steps and calculations""",
            context=initial_analysis
        )
        span_extraction_attempt = self.generate(
            instruction=f"""Attempt to solve using span extraction:
            - Identify relevant text spans from: {initial_analysis}
            - Ensure exact match with passage content
            - Provide extracted span as answer""",
            context=initial_analysis
        )
        attempts = await asyncio.gather(arithmetic_attempt, span_extraction_attempt)

        # Step 3: Validation - Check each attempt against problem constraints
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate this solution attempt:
                - Does it answer the question?
                - Are all constraints satisfied?
                - Is the format correct?""",
                context=attempt
            ) for attempt in attempts]
        )

        # Step 4: Synthesis - Select the best solution or synthesize insights
        synthesis = await self.ensemble(
            instruction="Select the most valid solution or combine insights from multiple attempts.",
            contexts_list=validations
        )

        # Step 5: Refinement - Iteratively improve the selected solution
        refined_solution = await self.revise(
            instruction="Refine the solution for clarity, accuracy, and completeness.",
            context=synthesis
        )

        # Step 6: Final Output - Format the answer appropriately
        final_answer = await self.generate(
            instruction=f"""Format the final answer:
            - If numerical, provide only the number
            - If span extraction, ensure exact match with passage
            - Include units or qualifiers if applicable
            Solution to refine: {refined_solution}""",
            context=refined_solution
        )

        return final_answer