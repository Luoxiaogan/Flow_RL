# Workflow ID: drop_210_0
# Benchmark: drop
# Data Indices: [397, 371]

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

        # Step 1: Extract all entities, numbers, and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references in the question
        references = await self.generate(
            instruction=f"""Resolve all pronouns and partial references in the question to specific entities:
            Passage Entities: {entities}
            Question References: [identify pronouns and partial names]""",
            context=entities
        )

        # Step 3: Identify the required operation(s)
        operation_type = await self.generate(
            instruction=f"""Classify the problem type and identify required operations:
            Passage: [contextual information]
            Question: [question text]
            Resolved References: {references}
            Possible Operations: addition, subtraction, counting, comparison, span extraction""",
            context=references
        )

        # Step 4: Execute operations dynamically
        if "count" in operation_type.lower():
            counts = await asyncio.gather(
                self.generate(instruction="Count occurrences of relevant entities...", context=entities),
                self.generate(instruction="Count specific actions or events...", context=entities)
            )
            result = await self.ensemble(
                instruction="Combine counts into final answer",
                contexts_list=counts
            )
        elif "comparison" in operation_type.lower():
            comparisons = await asyncio.gather(
                self.generate(instruction="Extract values for comparison...", context=entities),
                self.generate(instruction="Compare values logically...", context=entities)
            )
            result = await self.ensemble(
                instruction="Determine the correct comparison result",
                contexts_list=comparisons
            )
        elif "arithmetic" in operation_type.lower():
            arithmetic = await asyncio.gather(
                self.generate(instruction="Perform addition/subtraction...", context=entities),
                self.generate(instruction="Validate intermediate results...", context=entities)
            )
            result = await self.ensemble(
                instruction="Synthesize arithmetic results into final answer",
                contexts_list=arithmetic
            )
        else:  # Span extraction
            result = await self.generate(
                instruction="Extract the exact text span matching the question...",
                context=entities
            )

        # Step 5: Format the final answer
        final_answer = await self.generate(
            instruction=f"""Format the final answer according to expected output:
            Result: {result}
            Expected Format: number, date, or exact text span""",
            context=result
        )

        return final_answer