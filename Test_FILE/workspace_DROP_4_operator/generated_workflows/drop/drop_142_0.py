# Workflow ID: drop_142_0
# Benchmark: drop
# Data Indices: [280, 176]

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

        # Step 1: Extract all named entities, numbers, and relationships
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as structured list with categories.""",
            context=""
        )

        # Step 2: Classify the problem type
        problem_classification = await self.generate(
            instruction=f"""Classify the problem based on the question:
            Given entities and numbers: {entities_extraction}
            
            Determine if the problem is:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/longer, more, first/last, etc.)
            - Span Extraction (who did, what was the name of, when did, etc.)
            Provide clear classification.""",
            context=entities_extraction
        )

        # Step 3: Parallel processing for different problem types
        arithmetic_solution = await self.generate(
            instruction=f"""Solve arithmetic problems:
            Given entities and numbers: {entities_extraction}
            
            Perform required calculations (addition, subtraction, etc.) based on the question.
            Show all steps and present final answer.""",
            context=problem_classification
        )

        counting_solution = await self.generate(
            instruction=f"""Solve counting problems:
            Given entities and numbers: {entities_extraction}
            
            Count occurrences of specific entities or events based on the question.
            Show all steps and present final answer.""",
            context=problem_classification
        )

        comparison_solution = await self.generate(
            instruction=f"""Solve comparison problems:
            Given entities and numbers: {entities_extraction}
            
            Compare values and determine which is greater/longer, more, first/last, etc.
            Show all steps and present final answer.""",
            context=problem_classification
        )

        span_extraction_solution = await self.generate(
            instruction=f"""Solve span extraction problems:
            Given entities and numbers: {entities_extraction}
            
            Extract exact text spans from the passage based on the question.
            Ensure the span matches the passage exactly.""",
            context=problem_classification
        )

        # Step 4: Synthesize results using ensemble
        synthesis = await self.ensemble(
            instruction=f"""Synthesize results from different problem types:
            Arithmetic Solution: {arithmetic_solution}
            Counting Solution: {counting_solution}
            Comparison Solution: {comparison_solution}
            Span Extraction Solution: {span_extraction_solution}
            
            Select the best answer based on problem classification and validation criteria.""",
            contexts_list=[arithmetic_solution, counting_solution, comparison_solution, span_extraction_solution]
        )

        # Step 5: Validate and refine the final answer
        final_answer = await self.revise(
            instruction=f"""Validate and refine the final answer:
            Synthesized Result: {synthesis}
            
            Ensure the answer matches the expected format (number, date, exact text span).
            Double-check calculations and logical consistency.""",
            context=synthesis
        )

        return final_answer