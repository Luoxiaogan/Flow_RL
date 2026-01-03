# Workflow ID: drop_235_0
# Benchmark: drop
# Data Indices: [97, 87]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and classify question type
        initial_analysis = await self.generate(
            instruction="""Extract all relevant information from the passage and question:
            - Identify named entities (people, places, organizations)
            - Extract numerical values and their context
            - Classify the question type (arithmetic, counting, comparison, span extraction)
            - Identify potential references (pronouns, partial names) and their likely targets
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Processing - Resolve references, execute operations, validate
        reference_resolution, operation_execution, validation = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve all references in the question:
                - Map pronouns and partial names to specific entities in the passage
                - Ensure consistency across the entire question
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Execute the required operation(s) based on the question type:
                - Perform arithmetic calculations if needed
                - Count occurrences accurately
                - Compare values or spans as specified
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Validate intermediate results:
                - Check for consistency and completeness
                - Ensure all relevant information is considered
                Context: {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Step 3: Conditional Branching - Handle different question types
        if "arithmetic" in initial_analysis.lower():
            refined_result = await self.revise(
                instruction="Ensure precise calculation and double-check arithmetic.",
                context=operation_execution
            )
        elif "counting" in initial_analysis.lower():
            refined_result = await self.revise(
                instruction="Verify that all instances are counted and no duplicates are included.",
                context=operation_execution
            )
        else:
            refined_result = operation_execution

        # Step 4: Synthesis and Final Answer
        final_answer = await self.ensemble(
            instruction="""Synthesize all results into the final answer:
            - Combine resolved references, executed operations, and validation checks
            - Format the answer according to the expected output (number, date, text span)
            - Ensure the answer is consistent with the passage and question""",
            contexts_list=[reference_resolution, refined_result, validation]
        )

        return final_answer