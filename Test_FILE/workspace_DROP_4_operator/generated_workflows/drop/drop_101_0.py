# Workflow ID: drop_101_0
# Benchmark: drop
# Data Indices: [333, 467]

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

        # Step 1: Parallel Information Extraction
        extraction_tasks = await asyncio.gather(
            self.generate(
                instruction="Extract all named entities (people, places, organizations) and their roles.",
                context=""
            ),
            self.generate(
                instruction="Extract all numbers and their associated contexts (e.g., '10-yard TD pass').",
                context=""
            ),
            self.generate(
                instruction="Identify relationships and actions described in the passage.",
                context=""
            )
        )
        structured_context = "\n".join(extraction_tasks)

        # Step 2: Question Analysis and Operation Identification
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and determine the required operation(s):
            - Is it numerical (addition, subtraction, counting)?
            - Is it comparative (greater than, less than)?
            - Is it a span extraction (exact text match)?
            Provide detailed reasoning and identify all relevant entities/numbers from the context.
            Structured Context: {structured_context}""",
            context=structured_context
        )

        # Step 3: Execute Operations
        operation_result = await self.generate(
            instruction=f"""Based on the analysis:
            {question_analysis}
            
            Perform the required operation(s) and compute the result. Ensure all steps are clearly documented.""",
            context=question_analysis
        )

        # Step 4: Validation and Refinement
        validation = await self.generate(
            instruction=f"""Validate the computed result:
            - Does it make sense given the context?
            - Are all relevant entities/numbers accounted for?
            If issues are found, suggest corrections.
            Operation Result: {operation_result}""",
            context=operation_result
        )
        if "error" in validation.lower() or "issue" in validation.lower():
            refined_result = await self.revise(
                instruction=f"""Refine the operation result based on validation feedback:
                Feedback: {validation}""",
                context=operation_result
            )
            operation_result = refined_result

        # Step 5: Ensemble-Based Answer Selection
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a concise answer based on the operation result:
                Operation Result: {operation_result}""",
                context=operation_result
            ),
            self.generate(
                instruction=f"""Generate an alternative interpretation or phrasing of the answer:
                Operation Result: {operation_result}""",
                context=operation_result
            )
        )
        final_answer = await self.ensemble(
            instruction="""Select the best answer based on:
            - Relevance to the question
            - Precision and correctness
            - Consistency with the passage""",
            contexts_list=candidate_answers
        )

        return final_answer