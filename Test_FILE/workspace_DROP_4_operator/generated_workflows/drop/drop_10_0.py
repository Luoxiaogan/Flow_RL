# Workflow ID: drop_10_0
# Benchmark: drop
# Data Indices: [229, 170]

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
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve pronouns and partial names in the question:
            Entities: {entities}
            Map 'they', 'the team', etc., to specific entities.""",
            context=entities
        )

        # Step 3: Identify the required operation
        operation_type = await self.generate(
            instruction=f"""Classify the question into one of the following categories:
            - Arithmetic (addition, subtraction, counting)
            - Comparison (greater, longer, more)
            - Span Extraction (who, what, when)
            Entities: {entities}
            Resolved References: {resolved_references}""",
            context=resolved_references
        )

        # Step 4: Execute the operation
        if "arithmetic" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Entities: {entities}
                Operation Type: {operation_type}""",
                context=operation_type
            )
        elif "comparison" in operation_type.lower():
            candidates = await asyncio.gather(
                self.generate(instruction="Extract first value...", context=entities),
                self.generate(instruction="Extract second value...", context=entities)
            )
            result = await self.ensemble(
                instruction="Compare values and determine which is greater/longer...",
                contexts_list=candidates
            )
        elif "span" in operation_type.lower():
            candidates = await asyncio.gather(
                self.generate(instruction="Extract first candidate span...", context=entities),
                self.generate(instruction="Extract second candidate span...", context=entities)
            )
            result = await self.ensemble(
                instruction="Select the best matching span...",
                contexts_list=candidates
            )
        else:
            result = await self.generate(
                instruction=f"""Handle miscellaneous question type:
                Entities: {entities}
                Operation Type: {operation_type}""",
                context=operation_type
            )

        # Step 5: Validate and refine the result
        validation = await self.revise(
            instruction=f"""Validate the result:
            Entities: {entities}
            Operation Type: {operation_type}
            Result: {result}""",
            context=result
        )

        # Iterative refinement if necessary
        for _ in range(2):
            if "error" in validation.lower():
                result = await self.revise(
                    instruction=f"""Refine the result based on validation feedback:
                    Feedback: {validation}
                    Current Result: {result}""",
                    context=result
                )
                validation = await self.revise(
                    instruction="Re-validate the refined result...",
                    context=result
                )
            else:
                break

        return result