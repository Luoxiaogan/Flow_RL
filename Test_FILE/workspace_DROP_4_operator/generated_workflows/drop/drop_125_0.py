# Workflow ID: drop_125_0
# Benchmark: drop
# Data Indices: [28, 391]

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

        # Step 1: Extract all relevant entities and numbers
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve all references in the question:
            - Identify pronouns and partial names
            - Map them to specific entities in the passage
            Passage Entities: {entities}""",
            context=""
        )

        # Step 3: Classify the question type and identify required operations
        question_type = await self.generate(
            instruction=f"""Classify the question type and identify required operations:
            - Is it numerical, logical, or textual?
            - Does it require addition, subtraction, counting, comparison, or span extraction?
            Resolved References: {resolved_references}""",
            context=""
        )

        # Step 4: Execute the required operation(s)
        if "numerical" in question_type.lower():
            # Parallel execution for numerical operations
            operations = await asyncio.gather(
                self.generate(
                    instruction="Perform addition or counting based on the question...",
                    context=resolved_references
                ),
                self.generate(
                    instruction="Perform subtraction or comparison based on the question...",
                    context=resolved_references
                )
            )
            result = await self.ensemble(
                instruction="Select the most accurate numerical result...",
                contexts_list=operations
            )
        elif "textual" in question_type.lower():
            result = await self.generate(
                instruction="Extract the exact text span matching the question...",
                context=resolved_references
            )
        else:
            # Default comprehensive approach
            result = await self.generate(
                instruction="Solve using general reasoning...",
                context=resolved_references
            )

        # Step 5: Validate and refine the result
        validated_result = await self.revise(
            instruction="Validate the result and improve clarity or accuracy...",
            context=result
        )

        # Step 6: Format the final answer
        final_answer = await self.revise(
            instruction="Format the answer to match the expected output format...",
            context=validated_result
        )

        return final_answer