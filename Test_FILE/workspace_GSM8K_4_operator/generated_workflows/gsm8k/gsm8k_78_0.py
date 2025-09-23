# Workflow ID: gsm8k_78_0
# Benchmark: gsm8k
# Data Indices: [82, 146]

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

        # Step 1: Extract key information
        extraction = await self.generate(
            instruction="""Extract all numerical values, units, and relationships:
            - Numbers: List all explicit numerical values with their context.
            - Units: Identify units associated with each number.
            - Relationships: Describe how numbers relate to each other (e.g., rates, proportions).""",
            context=""
        )

        # Step 2: Classify the problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {extraction}
            - Is it sequential, rate-based, proportional, or distribution-focused?
            - What is the expected answer format?""",
            context=extraction
        )

        # Step 3: Generate multiple solution plans in parallel
        plan_1 = self.generate(
            instruction=f"""Develop a solution plan focusing on sequential operations:
            {classification}
            - List all steps explicitly.
            - Show intermediate calculations.""",
            context=classification
        )
        plan_2 = self.generate(
            instruction=f"""Develop a solution plan focusing on proportional reasoning:
            {classification}
            - Highlight scaling factors or ratios.
            - Show intermediate calculations.""",
            context=classification
        )
        plans = await asyncio.gather(plan_1, plan_2)

        # Step 4: Synthesize the best plan
        best_plan = await self.ensemble(
            instruction="""Select the most appropriate plan:
            - Consider clarity, completeness, and alignment with the problem type.
            - Resolve any conflicts between plans.""",
            contexts_list=plans
        )

        # Step 5: Execute the plan step-by-step
        execution = await self.generate(
            instruction=f"""Execute the selected plan step-by-step:
            {best_plan}
            - Perform calculations explicitly.
            - Validate intermediate results.""",
            context=best_plan
        )

        # Step 6: Validate and refine the solution
        validation = await self.generate(
            instruction=f"""Validate the solution:
            {execution}
            - Check for consistency with the problem statement.
            - Ensure all constraints are satisfied.""",
            context=execution
        )
        refined_solution = await self.revise(
            instruction="Refine the solution to ensure clarity and precision.",
            context=validation
        )

        # Step 7: Summarize the final answer
        final_answer = await self.summarize(
            instruction="""Condense the solution into a single numerical answer:
            - Include the final value and its unit, if applicable.
            - Ensure the format matches the problem requirements.""",
            context=refined_solution
        )

        return final_answer