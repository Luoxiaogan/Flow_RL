# Workflow ID: drop_241_0
# Benchmark: drop
# Data Indices: [433, 479]

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

        # Step 1: Initial Analysis (Parallel Fork)
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: People, teams, locations
            - Numbers: Values and what they represent
            - Relationships: Actions and connections between entities""",
            context=""
        )
        question_type_task = self.generate(
            instruction="""Classify the question type:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span extraction""",
            context=""
        )
        initial_analysis = await asyncio.gather(entities_task, question_type_task)
        entities, question_type = initial_analysis

        # Step 2: Reference Resolution and Operation Classification (Conditional Branching)
        if "arithmetic" in question_type.lower():
            operation = "Perform arithmetic operations as implied by the question."
        elif "counting" in question_type.lower():
            operation = "Count the occurrences of specified entities or events."
        elif "comparison" in question_type.lower():
            operation = "Compare values or entities as implied by the question."
        else:
            operation = "Extract the exact text span matching the question."

        resolved_references = await self.revise(
            instruction=f"""Resolve all pronouns and partial names in the passage:
            - Ensure each reference points to the correct entity
            - Use context from the passage and extracted entities""",
            context=entities
        )

        # Step 3: Computation (Parallel Execution)
        if "arithmetic" in question_type.lower() or "counting" in question_type.lower():
            computation_task_1 = self.generate(
                instruction=f"""Execute the identified operation using the resolved references:
                {operation}""",
                context=resolved_references
            )
            computation_task_2 = self.generate(
                instruction=f"""Re-execute the operation to validate consistency:
                {operation}""",
                context=resolved_references
            )
            computations = await asyncio.gather(computation_task_1, computation_task_2)
        else:
            computation_task = self.generate(
                instruction=f"""Extract the exact text span matching the question:
                {operation}""",
                context=resolved_references
            )
            computations = [await computation_task]

        # Step 4: Ensemble Decision (Merge)
        final_answer = await self.ensemble(
            instruction="""Select the best answer:
            - Matches the expected format (number, date, text span)
            - Is consistent with the passage
            - Resolves all ambiguities""",
            contexts_list=computations
        )

        # Step 5: Feedback Loop (Iterative Refinement)
        for _ in range(2):  # Limit iterations to avoid excessive latency
            validation = await self.generate(
                instruction=f"""Validate the final answer:
                - Does it match the question requirements?
                - Is it consistent with the passage?""",
                context=final_answer
            )
            if "error" in validation.lower():
                final_answer = await self.revise(
                    instruction=f"""Refine the answer based on validation feedback:
                    {validation}""",
                    context=final_answer
                )
            else:
                break

        return final_answer