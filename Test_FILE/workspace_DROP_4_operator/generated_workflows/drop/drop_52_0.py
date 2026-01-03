# Workflow ID: drop_52_0
# Benchmark: drop
# Data Indices: [478, 183]

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

        # Step 1: Initial Analysis - Extract entities and classify question type
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Classify the question type based on its phrasing:
            - Span extraction: 'Who', 'What', 'When'
            - Arithmetic: 'How many', 'What is the difference'
            - Comparison: 'Which is greater', 'Who had more'
            - Multi-step: Questions requiring chaining operations
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Processing - Extract spans and resolve references
        spans_task = self.generate(
            instruction="Extract relevant spans from the passage that match the question's focus.",
            context=initial_analysis
        )
        references_task = self.generate(
            instruction="Resolve question references (e.g., pronouns) to specific entities in the passage.",
            context=initial_analysis
        )
        spans, references = await asyncio.gather(spans_task, references_task)

        # Step 3: Conditional Branching - Solve based on question type
        question_type = await self.generate(
            instruction="Identify the question type from the initial analysis.",
            context=initial_analysis
        )

        if "span extraction" in question_type.lower():
            solution = await self.generate(
                instruction="Extract the exact text span from the passage that answers the question.",
                context=f"{spans}

{references}"
            )
        elif "arithmetic" in question_type.lower():
            solution = await self.generate(
                instruction="Perform the required arithmetic operation(s) using numbers from the passage.",
                context=f"{spans}

{references}"
            )
        elif "comparison" in question_type.lower():
            solution = await self.generate(
                instruction="Compare the relevant numbers or entities from the passage.",
                context=f"{spans}

{references}"
            )
        else:  # Multi-step reasoning
            solution = await self.generate(
                instruction="Chain multiple operations together to answer the question.",
                context=f"{spans}

{references}"
            )

        # Step 4: Validation and Refinement
        validation = await self.generate(
            instruction="Validate the solution against the passage and question. Identify inconsistencies.",
            context=solution
        )
        if "inconsistent" in validation.lower():
            refined_solution = await self.revise(
                instruction="Refine the solution to address inconsistencies.",
                context=solution
            )
            solution = refined_solution

        # Step 5: Output Formatting
        formatted_answer = await self.generate(
            instruction="Format the solution to match the expected output type (number, date, or text span).",
            context=solution
        )

        return formatted_answer