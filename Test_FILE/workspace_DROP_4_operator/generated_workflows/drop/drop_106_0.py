# Workflow ID: drop_106_0
# Benchmark: drop
# Data Indices: [246, 398]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract all relevant information from the passage:
            - Named entities (people, places, organizations)
            - Numbers and their contexts
            - Relationships between entities
            - Resolve pronouns and partial references
            
            Classify the question type:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/longer, more, first/last, etc.)
            - Span extraction (who did, what was, when did, etc.)
            - Multi-step reasoning (chaining multiple facts/operations)""",
            context=""
        )

        # Step 2: Parallel Exploration
        question_type = await self.generate(
            instruction="Identify the primary question type from the analysis.",
            context=analysis
        )

        async def arithmetic_path():
            return await self.generate(
                instruction=f"""Solve the arithmetic problem:
                - Identify relevant numbers from the passage
                - Perform the required operation (addition, subtraction, etc.)
                - Present the final result with appropriate units""",
                context=analysis
            )

        async def counting_path():
            return await self.generate(
                instruction=f"""Count the instances of the target entity:
                - Identify the target entity from the question
                - Find all occurrences in the passage
                - Compute the total count""",
                context=analysis
            )

        async def comparison_path():
            return await self.generate(
                instruction=f"""Compare the relevant metrics:
                - Identify the entities or values to compare
                - Determine the relationship (greater, less, equal)
                - Present the result clearly""",
                context=analysis
            )

        async def span_extraction_path():
            return await self.generate(
                instruction=f"""Extract the exact text span:
                - Identify the target phrase or entity
                - Match it precisely to the passage
                - Ensure the span is complete and accurate""",
                context=analysis
            )

        # Execute relevant paths based on question type
        paths = []
        if "arithmetic" in question_type.lower():
            paths.append(arithmetic_path())
        if "counting" in question_type.lower():
            paths.append(counting_path())
        if "comparison" in question_type.lower():
            paths.append(comparison_path())
        if "span" in question_type.lower():
            paths.append(span_extraction_path())

        candidates = await asyncio.gather(*paths)

        # Step 3: Validation and Ensemble
        final_answer = await self.ensemble(
            instruction="""Select the best answer:
            - Matches the expected format (number, date, text span)
            - Logically consistent with the passage and question
            - Complete and precise""",
            contexts_list=candidates
        )

        return final_answer