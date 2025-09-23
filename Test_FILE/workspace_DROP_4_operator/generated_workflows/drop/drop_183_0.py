# Workflow ID: drop_183_0
# Benchmark: drop
# Data Indices: [469, 146]

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

        # Step 1: Extract entities, numbers, and relationships
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage and question.
            Format as a structured list:
            - Entities: [names, roles]
            - Numbers: [values, what they represent]
            - Relationships: [connections between entities/numbers]""",
            context=""
        )

        # Step 2: Resolve references (pronouns, partial names)
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities:
            Passage: {self.problem_text}
            Extracted Information: {extraction}""",
            context=extraction
        )

        # Step 3: Classify problem type and identify required operations
        classification = await self.generate(
            instruction=f"""Classify the problem type and identify required operations:
            Passage: {self.problem_text}
            Extracted Information: {extraction}
            Resolved References: {resolved_references}
            Output format:
            - Problem Type: [arithmetic, counting, comparison, etc.]
            - Required Operations: [addition, subtraction, etc.]""",
            context=resolved_references
        )

        # Step 4: Execute operations in parallel
        operations = ["addition", "subtraction", "counting", "comparison"]  # Example operations
        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Perform the following operation based on the extracted information:
                Operation: {op}
                Passage: {self.problem_text}
                Extracted Information: {extraction}
                Resolved References: {resolved_references}""",
                context=classification
            ) for op in operations]
        )

        # Step 5: Validate and synthesize results
        validation = await self.generate(
            instruction=f"""Validate the results of each operation:
            Operations Results: {operation_results}
            Passage: {self.problem_text}
            Extracted Information: {extraction}
            Resolved References: {resolved_references}""",
            context="\n".join(operation_results)
        )

        final_answer = await self.ensemble(
            instruction="""Synthesize the validated results into a final answer.
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            contexts_list=operation_results + [validation]
        )

        # Step 6: Feedback loop for iterative refinement
        for _ in range(3):  # Allow up to 3 refinement iterations
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    Validation: {validation}
                    Current Answer: {final_answer}""",
                    context=final_answer
                )
                final_answer = refined
                validation = await self.generate(
                    instruction="Re-validate the refined solution.",
                    context=refined
                )
            else:
                break

        return final_answer