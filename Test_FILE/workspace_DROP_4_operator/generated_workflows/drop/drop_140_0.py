# Workflow ID: drop_140_0
# Benchmark: drop
# Data Indices: [9, 261]

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

        # Phase 1: Analysis
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        resolved_references = await self.revise(
            instruction=f"Resolve pronouns and partial names to their corresponding entities:\n{entities}",
            context=entities
        )
        problem_type = await self.generate(
            instruction=f"""Classify the problem type based on the question:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/longer, first/last, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            Entities and references:\n{resolved_references}""",
            context=resolved_references
        )

        # Phase 2: Execution
        if "arithmetic" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Identify numbers and operations from the passage
                - Execute the calculation step-by-step
                Problem type:\n{problem_type}""",
                context=resolved_references
            )
        elif "counting" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event:
                - Identify the target entity or event
                - Count all instances in the passage
                Problem type:\n{problem_type}""",
                context=resolved_references
            )
        elif "comparison" in problem_type.lower():
            options = await asyncio.gather(
                self.generate(instruction="Identify the first value or span to compare", context=resolved_references),
                self.generate(instruction="Identify the second value or span to compare", context=resolved_references)
            )
            result = await self.ensemble(
                instruction="Compare the two values or spans and determine the correct answer",
                contexts_list=options
            )
        elif "span extraction" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                - Match the phrasing in the question to the passage
                Problem type:\n{problem_type}""",
                context=resolved_references
            )
        else:
            result = await self.generate(
                instruction="Apply general problem-solving framework to derive the answer",
                context=resolved_references
            )

        # Phase 3: Validation
        validation = await self.generate(
            instruction=f"""Validate the answer against the passage:
            - Check if the answer matches the expected format
            - Verify correctness by cross-referencing with the passage
            Result:\n{result}""",
            context=resolved_references
        )
        if "error" in validation.lower():
            corrected_result = await self.revise(
                instruction=f"Fix errors identified during validation:\n{validation}",
                context=result
            )
            final_answer = corrected_result
        else:
            final_answer = result

        return final_answer