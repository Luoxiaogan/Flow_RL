# Workflow ID: drop_71_0
# Benchmark: drop
# Data Indices: [73, 91]

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

        # Step 1: Extract all relevant entities, numbers, and relationships
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Classify the question type and identify required operation(s)
        question_analysis = await self.generate(
            instruction="""Classify the question type and identify the required operation(s):
            - Arithmetic: Addition, subtraction, counting
            - Comparison: Greater than, less than, equal to
            - Span Extraction: Exact text spans
            Provide a clear classification and describe the required steps.""",
            context=""
        )

        # Step 3: Execute the identified operation(s)
        # Dynamically construct instructions based on question analysis
        operation_execution = await self.generate(
            instruction=f"""Based on the question analysis:
            {question_analysis}
            
            Execute the required operation(s) using the extracted entities and numbers:
            {entities_extraction}
            
            Ensure all steps are clearly documented and validated.""",
            context=f"{entities_extraction}

{question_analysis}"
        )

        # Step 4: Validate and refine results iteratively
        refined_result = operation_execution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"Validate the result: {refined_result}. Identify any errors or missing steps.",
                context=refined_result
            )
            if "error" not in validation.lower():
                break
            refined_result = await self.revise(
                instruction=f"Fix issues: {validation}",
                context=refined_result
            )

        # Step 5: Format the final answer
        final_answer = await self.generate(
            instruction=f"""Format the final answer based on the refined result:
            {refined_result}
            
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            context=refined_result
        )

        return final_answer