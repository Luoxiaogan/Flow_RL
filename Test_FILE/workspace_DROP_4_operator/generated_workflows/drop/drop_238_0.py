# Workflow ID: drop_238_0
# Benchmark: drop
# Data Indices: [192, 37]

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
            instruction="""Extract all named entities, numbers, relationships, and constraints from the passage. 
            Then classify the question type (arithmetic, counting, comparison, span extraction, multi-step reasoning). 
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Reference Resolution - Map question references to passage entities
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial references in the question by mapping them to entities in the passage. 
            Use the following analysis as context: {initial_analysis}""",
            context=initial_analysis
        )

        # Step 3: Operation Execution - Perform required operations based on question type
        question_type = await self.generate(
            instruction="Identify the question type and determine the required operations.",
            context=resolved_references
        )

        if "arithmetic" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Perform the necessary arithmetic operations (addition, subtraction, etc.) using the following context: 
                {resolved_references}""",
                context=resolved_references
            )
        elif "counting" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Count the relevant instances or entities using the following context: 
                {resolved_references}""",
                context=resolved_references
            )
        elif "comparison" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Compare the relevant entities or values using the following context: 
                {resolved_references}""",
                context=resolved_references
            )
        elif "span extraction" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question using the following context: 
                {resolved_references}""",
                context=resolved_references
            )
        else:  # Multi-step reasoning
            operation_result = await self.generate(
                instruction=f"""Chain multiple operations to solve the problem using the following context: 
                {resolved_references}""",
                context=resolved_references
            )

        # Step 4: Validation and Formatting - Ensure the answer matches the expected format
        validated_answer = await self.revise(
            instruction="Validate the answer format (number, date, or exact text span). Correct any issues.",
            context=operation_result
        )

        # Step 5: Iterative Refinement - Detect and correct errors
        refined_answer = validated_answer
        for _ in range(3):  # Allow up to 3 refinement iterations
            error_check = await self.generate(
                instruction="Check for errors or ambiguities in the answer.",
                context=refined_answer
            )
            if "error" in error_check.lower():
                refined_answer = await self.revise(
                    instruction=f"Fix the identified issues: {error_check}",
                    context=refined_answer
                )
            else:
                break

        # Step 6: Final Synthesis - Combine multiple perspectives if needed
        final_answer = await self.ensemble(
            instruction="Synthesize the final answer from all available information.",
            contexts_list=[validated_answer, refined_answer]
        )

        return final_answer