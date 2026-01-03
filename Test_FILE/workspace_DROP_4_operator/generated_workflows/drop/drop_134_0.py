# Workflow ID: drop_134_0
# Benchmark: drop
# Data Indices: [90, 453]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and classify problem
        analysis = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage. 
            Classify the problem type (e.g., arithmetic, counting, comparison, span extraction). 
            Resolve any pronouns or partial names to specific entities. 
            Provide a structured summary of findings.""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore different solution strategies
        arithmetic_solution = await self.generate(
            instruction=f"""Based on the analysis: {analysis}
            Solve the problem using arithmetic operations (addition, subtraction, etc.). 
            Ensure all calculations are precise and validated.""",
            context=analysis
        )
        counting_solution = await self.generate(
            instruction=f"""Based on the analysis: {analysis}
            Solve the problem by counting relevant instances in the passage. 
            Ensure no instances are missed and provide justification for each count.""",
            context=analysis
        )
        span_extraction_solution = await self.generate(
            instruction=f"""Based on the analysis: {analysis}
            Extract the exact text span from the passage that answers the question. 
            Ensure the span matches the passage exactly and adheres to the question's constraints.""",
            context=analysis
        )

        # Step 3: Conditional Branching - Select the best strategy
        best_strategy = await self.ensemble(
            instruction="""Evaluate the following solutions and select the most appropriate one:
            - Arithmetic solution: {arithmetic_solution}
            - Counting solution: {counting_solution}
            - Span extraction solution: {span_extraction_solution}
            Consider the problem type, accuracy, and adherence to constraints.""",
            contexts_list=[arithmetic_solution, counting_solution, span_extraction_solution]
        )

        # Step 4: Iterative Refinement - Validate and refine the selected solution
        refined_solution = best_strategy
        for _ in range(2):  # Perform up to 2 iterations of refinement
            validation = await self.generate(
                instruction=f"""Validate the following solution: {refined_solution}
                Identify any errors, ambiguities, or areas for improvement.""",
                context=refined_solution
            )
            if "error" in validation.lower() or "improve" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution based on the following feedback: {validation}
                    Correct errors, resolve ambiguities, and improve clarity.""",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Synthesis - Format the answer appropriately
        final_answer = await self.summarize(
            instruction=f"""Synthesize the refined solution: {refined_solution}
            Format the answer to match the expected output (number, date, or exact text span).""",
            context=refined_solution
        )

        return final_answer