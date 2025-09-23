# Workflow ID: drop_23_0
# Benchmark: drop
# Data Indices: [392, 128]

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
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Analyze question structure
        question_analysis_task = self.generate(
            instruction="""Classify the question type:
            - Is it numerical (addition, subtraction, counting)?
            - Is it a span extraction (who, what, when)?
            - Does it require multi-hop reasoning?
            Provide a structured classification.""",
            context=""
        )

        # Run extraction and analysis in parallel
        entities, question_analysis = await asyncio.gather(entities_task, question_analysis_task)

        # Step 3: Resolve references
        resolved_references = await self.revise(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities:
            Passage Entities: {entities}
            Ensure all references are unambiguous.""",
            context=question_analysis
        )

        # Step 4: Perform operations based on question type
        if "numerical" in question_analysis.lower():
            # Handle arithmetic or counting
            result = await self.generate(
                instruction=f"""Perform the required numerical operation:
                Extracted Numbers: {entities}
                Resolved References: {resolved_references}
                Show all steps and present the final answer.""",
                context=resolved_references
            )
        elif "span extraction" in question_analysis.lower():
            # Handle exact text span extraction
            result = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question:
                Passage: {self.problem_text}
                Resolved References: {resolved_references}""",
                context=resolved_references
            )
        else:
            # Default to general reasoning
            result = await self.generate(
                instruction=f"""Answer the question using the provided information:
                Passage Entities: {entities}
                Resolved References: {resolved_references}""",
                context=resolved_references
            )

        # Step 5: Validate and format the answer
        final_answer = await self.revise(
            instruction=f"""Ensure the answer is correct and matches the expected format:
            - Numerical answers should be precise and include units if applicable.
            - Span answers should match the passage exactly.
            Original Answer: {result}""",
            context=result
        )

        return final_answer