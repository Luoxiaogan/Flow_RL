# Workflow ID: drop_181_0
# Benchmark: drop
# Data Indices: [81, 277]

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
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify it:
            - Is it numerical, logical, or textual?
            - Does it require counting, comparison, arithmetic, or span extraction?
            - What is the expected answer format?
            Provide structured classification.""",
            context=""
        )

        # Step 2: Entity and Number Extraction
        entities_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=initial_analysis
        )

        # Step 3: Reference Resolution
        resolved_references = await self.revise(
            instruction="""Resolve pronouns and partial names to their correct entities:
            - Cross-check resolutions against the context
            - Ensure accuracy by validating against the passage""",
            context=entities_numbers
        )

        # Step 4: Operation Identification and Execution
        operation_identification = await self.generate(
            instruction=f"""Based on the question and resolved references:
            {resolved_references}
            
            Identify the required operation(s):
            - Counting: How many instances of X?
            - Comparison: Which is greater/longer?
            - Arithmetic: Addition, subtraction, etc.
            - Span Extraction: Exact text span matching
            
            Provide detailed instructions for executing the operation.""",
            context=resolved_references
        )

        # Parallelize execution of identified operations
        operation_results = await asyncio.gather(
            self.generate(
                instruction=f"Execute counting operations: {operation_identification}",
                context=resolved_references
            ),
            self.generate(
                instruction=f"Execute comparison operations: {operation_identification}",
                context=resolved_references
            ),
            self.generate(
                instruction=f"Execute arithmetic operations: {operation_identification}",
                context=resolved_references
            ),
            self.generate(
                instruction=f"Execute span extraction: {operation_identification}",
                context=resolved_references
            )
        )

        # Step 5: Answer Validation and Refinement
        validated_answer = await self.revise(
            instruction="""Validate the answer format:
            - Ensure it matches the expected format (number, date, or exact text span)
            - Refine if necessary to meet validation criteria""",
            context="\n".join(operation_results)
        )

        # Iterative refinement loop
        max_iterations = 3
        for _ in range(max_iterations):
            validation_check = await self.generate(
                instruction="Check if the answer meets all validation criteria.",
                context=validated_answer
            )
            if "error" not in validation_check.lower():
                break
            validated_answer = await self.revise(
                instruction=f"Refine based on validation feedback: {validation_check}",
                context=validated_answer
            )

        # Step 6: Final Output
        final_answer = await self.summarize(
            instruction="Summarize the final answer clearly and concisely.",
            context=validated_answer
        )

        return final_answer