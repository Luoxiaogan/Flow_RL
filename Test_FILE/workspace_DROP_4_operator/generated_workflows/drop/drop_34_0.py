# Workflow ID: drop_34_0
# Benchmark: drop
# Data Indices: [459, 8]

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

        # Step 1: Extract entities and numbers from the passage
        entity_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify the problem type
        problem_classification = await self.generate(
            instruction="""Classify the problem type based on the question:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Greater than, less than, etc.
            - Span Extraction: Who did, what was, etc.
            Provide a clear classification.""",
            context=entity_extraction
        )

        # Step 3: Resolve references (parallel processing)
        reference_resolution_1 = await self.generate(
            instruction=f"""Resolve pronouns and partial names in the passage:
            Entities: {entity_extraction}
            Question: What does 'they' refer to?""",
            context=entity_extraction
        )
        reference_resolution_2 = await self.generate(
            instruction=f"""Resolve ambiguous terms in the passage:
            Entities: {entity_extraction}
            Question: What does 'the team' refer to?""",
            context=entity_extraction
        )
        resolved_references = await self.ensemble(
            instruction="Select the most plausible interpretation for each reference.",
            contexts_list=[reference_resolution_1, reference_resolution_2]
        )

        # Step 4: Execute operations based on problem type (conditional branching)
        if "arithmetic" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Perform arithmetic operations:
                Entities: {entity_extraction}
                Resolved References: {resolved_references}
                Question: What calculations are needed?""",
                context=problem_classification
            )
        elif "counting" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Count instances or entities:
                Entities: {entity_extraction}
                Resolved References: {resolved_references}
                Question: What needs to be counted?""",
                context=problem_classification
            )
        elif "comparison" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Compare values or entities:
                Entities: {entity_extraction}
                Resolved References: {resolved_references}
                Question: What needs to be compared?""",
                context=problem_classification
            )
        else:  # Span extraction
            solution = await self.generate(
                instruction=f"""Extract exact text spans:
                Entities: {entity_extraction}
                Resolved References: {resolved_references}
                Question: What text span answers the question?""",
                context=problem_classification
            )

        # Step 5: Validate and refine the solution
        validation = await self.generate(
            instruction=f"""Validate the solution:
            Solution: {solution}
            Does it match the expected format and constraints?""",
            context=solution
        )
        refined_solution = await self.revise(
            instruction=f"""Refine the solution based on validation feedback:
            Validation: {validation}
            Original Solution: {solution}""",
            context=solution
        )

        return refined_solution