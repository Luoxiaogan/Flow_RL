# Workflow ID: drop_11_0
# Benchmark: drop
# Data Indices: [282, 284]

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
            - Entities: People, places, teams, etc.
            - Numbers: Values and their context
            - Relationships: Actions, events, and their connections
            Format as structured lists with clear categories.""",
            context=""
        )

        # Step 2: Problem Classification - Identify the type of question
        problem_classification = await self.generate(
            instruction=f"""Classify the problem based on the question:
            - Is it arithmetic (addition, subtraction, counting)?
            - Is it a comparison (greater/lesser, chronological order)?
            - Is it span extraction (who, what, when)?
            - Does it require multi-step reasoning?
            Provide a clear classification and reasoning.
            Context: {initial_analysis}""",
            context=initial_analysis
        )

        # Step 3: Parallel Solution Attempts - Generate multiple perspectives
        arithmetic_solution = await self.generate(
            instruction=f"""If the problem is arithmetic:
            - Perform the required calculations (addition, subtraction, counting).
            - Show all steps clearly.
            - Provide the final result.
            Context: {problem_classification}""",
            context=problem_classification
        )

        comparison_solution = await self.generate(
            instruction=f"""If the problem is a comparison:
            - Compare the relevant values or events.
            - Determine the greater/lesser value or chronological order.
            - Provide the final result.
            Context: {problem_classification}""",
            context=problem_classification
        )

        span_extraction_solution = await self.generate(
            instruction=f"""If the problem is span extraction:
            - Identify the exact text span from the passage.
            - Ensure the span matches the passage exactly.
            - Provide the final result.
            Context: {problem_classification}""",
            context=problem_classification
        )

        # Step 4: Validation and Refinement - Validate each solution attempt
        validation_results = await asyncio.gather(
            self.revise(
                instruction="Validate the arithmetic solution for correctness and completeness.",
                context=arithmetic_solution
            ),
            self.revise(
                instruction="Validate the comparison solution for correctness and completeness.",
                context=comparison_solution
            ),
            self.revise(
                instruction="Validate the span extraction solution for correctness and completeness.",
                context=span_extraction_solution
            )
        )

        # Step 5: Synthesis - Ensemble the refined solutions
        final_answer = await self.ensemble(
            instruction="""Select the best solution based on validation results:
            - Choose the most accurate and complete solution.
            - Ensure the answer matches the expected format.
            Provide the final answer.""",
            contexts_list=validation_results
        )

        return final_answer