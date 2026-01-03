# Workflow ID: drop_26_0
# Benchmark: drop
# Data Indices: [255, 238]

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

        # Step 1: Initial Analysis and Extraction
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        problem_type = await self.generate(
            instruction="""Classify the problem based on the question:
            - Is it arithmetic (addition, subtraction, etc.)?
            - Does it involve counting?
            - Is it a span extraction task?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Reference Resolution and Context Building
        resolved_context = await self.revise(
            instruction=f"""Resolve pronouns and partial references in the passage using the extracted entities:
            {extraction}
            Ensure all mentions are linked to their corresponding entities.""",
            context=extraction
        )

        # Step 3: Parallel Exploration of Solution Strategies
        strategies = {
            "arithmetic": """Perform arithmetic operations as suggested by the question. 
            Include addition, subtraction, and comparison.""",
            "counting": """Count instances as required by the question. 
            Consider different criteria for counting.""",
            "span_extraction": """Identify potential spans that answer the question. 
            Validate each span against the passage."""
        }

        solutions = await asyncio.gather(
            *[self.generate(
                instruction=strategies[stype],
                context=resolved_context
            ) for stype in strategies if stype in problem_type.lower()]
        )

        # Step 4: Synthesize Results
        final_answer = await self.ensemble(
            instruction="""Select the most plausible answer from the provided options. 
            Ensure the answer matches the question's requirements.""",
            contexts_list=solutions
        )

        # Step 5: Iterative Refinement and Validation
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the answer against the question:
                Question: {self.problem_text}
                Answer: {final_answer}
                Identify any discrepancies.""",
                context=final_answer
            )
            if "discrepancy" not in validation.lower():
                break
            final_answer = await self.revise(
                instruction=f"""Revise the answer to address the following issues:
                {validation}""",
                context=final_answer
            )

        return final_answer