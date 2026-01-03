# Workflow ID: drop_4_0
# Benchmark: drop
# Data Indices: [480, 462]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Identify people, places, teams, and other entities
            - Extract numerical values and their context
            - Map pronouns and partial names to specific entities
            - Highlight key events and actions
            Provide structured output.""",
            context=""
        )

        # Step 2: Question Classification - Determine the type of question and required operation(s)
        classification = await self.generate(
            instruction=f"""Classify the question based on the following criteria:
            - Is it arithmetic (addition, subtraction, etc.)?
            - Does it involve counting?
            - Is it a comparison (greater, less, first, last)?
            - Does it require exact span extraction?
            - Are multiple steps involved?
            Passage Context: {initial_analysis}
            Provide detailed classification and reasoning.""",
            context=initial_analysis
        )

        # Step 3: Parallel Operation Execution - Perform identified operations
        arithmetic_result = await self.generate(
            instruction=f"""If the question involves arithmetic:
            - Identify relevant numbers from the passage
            - Perform the required calculation
            Passage Context: {initial_analysis}
            Question Type: {classification}""",
            context=classification
        )
        counting_result = await self.generate(
            instruction=f"""If the question involves counting:
            - Identify instances of the target entity or event
            - Count occurrences accurately
            Passage Context: {initial_analysis}
            Question Type: {classification}""",
            context=classification
        )
        comparison_result = await self.generate(
            instruction=f"""If the question involves comparison:
            - Identify values or attributes to compare
            - Determine the relationship (greater, less, first, last)
            Passage Context: {initial_analysis}
            Question Type: {classification}""",
            context=classification
        )
        span_extraction_result = await self.generate(
            instruction=f"""If the question requires span extraction:
            - Locate the exact text span matching the query
            - Ensure it matches the passage exactly
            Passage Context: {initial_analysis}
            Question Type: {classification}""",
            context=classification
        )

        # Step 4: Ensemble - Combine results and select the best solution
        combined_results = await self.ensemble(
            instruction=f"""Evaluate the following results and select the best solution:
            - Arithmetic Result: {arithmetic_result}
            - Counting Result: {counting_result}
            - Comparison Result: {comparison_result}
            - Span Extraction Result: {span_extraction_result}
            Ensure the selected solution matches the question type and format.""",
            contexts_list=[arithmetic_result, counting_result, comparison_result, span_extraction_result]
        )

        # Step 5: Validation and Refinement - Verify and refine the solution
        refined_solution = await self.revise(
            instruction=f"""Validate the selected solution:
            - Check for correctness against the question
            - Ensure proper formatting (number, date, exact span)
            - Refine if necessary
            Selected Solution: {combined_results}""",
            context=combined_results
        )

        # Step 6: Summarize - Condense the final answer
        final_answer = await self.summarize(
            instruction=f"""Condense the refined solution into the final answer:
            - Remove unnecessary details
            - Maintain required format
            Refined Solution: {refined_solution}""",
            context=refined_solution
        )

        return final_answer