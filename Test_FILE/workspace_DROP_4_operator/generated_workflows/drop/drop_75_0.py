# Workflow ID: drop_75_0
# Benchmark: drop
# Data Indices: [410, 76]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list:
            - Entities: [names, roles, descriptions]
            - Numbers: [values, what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=""
        )

        # Step 2: Question Type Classification and Reference Resolution
        classification = await self.generate(
            instruction=f"""Classify the question type and resolve references:
            Passage Information: {initial_analysis}
            Classify into:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span Extraction
            Resolve pronouns and partial names to specific entities.""",
            context=initial_analysis
        )

        # Step 3: Parallel Solution Attempts
        arithmetic_attempt = self.generate(
            instruction=f"""Solve the problem assuming it requires arithmetic operations:
            Passage Information: {initial_analysis}
            Question Analysis: {classification}
            Perform all necessary calculations and provide the result.""",
            context=classification
        )
        span_extraction_attempt = self.generate(
            instruction=f"""Solve the problem assuming it requires span extraction:
            Passage Information: {initial_analysis}
            Question Analysis: {classification}
            Extract the exact text span that answers the question.""",
            context=classification
        )
        comparison_attempt = self.generate(
            instruction=f"""Solve the problem assuming it requires comparison:
            Passage Information: {initial_analysis}
            Question Analysis: {classification}
            Compare relevant entities or numbers and provide the result.""",
            context=classification
        )

        # Run parallel attempts
        results = await asyncio.gather(arithmetic_attempt, span_extraction_attempt, comparison_attempt)

        # Step 4: Validation and Refinement
        refined_results = []
        for result in results:
            validation = await self.generate(
                instruction=f"""Validate the solution:
                Passage Information: {initial_analysis}
                Solution: {result}
                Check for errors, ambiguities, or mismatches with the question requirements.""",
                context=result
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    Feedback: {validation}""",
                    context=result
                )
                refined_results.append(refined)
            else:
                refined_results.append(result)

        # Step 5: Ensemble Decision
        final_answer = await self.ensemble(
            instruction=f"""Select the best solution or synthesize multiple approaches:
            Solutions: {refined_results}
            Ensure the final answer matches the question's requirements and format.""",
            contexts_list=refined_results
        )

        return final_answer