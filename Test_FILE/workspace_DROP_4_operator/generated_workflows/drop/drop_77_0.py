# Workflow ID: drop_77_0
# Benchmark: drop
# Data Indices: [376, 379]

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

        # Step 1: Extract entities and numbers
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Analyze the question
        question_analysis = await self.generate(
            instruction="""Classify the question type and identify the required operation(s). 
            Consider arithmetic, counting, comparison, span extraction, and multi-step reasoning.
            Provide a structured analysis.""",
            context=entities_extraction
        )

        # Step 3: Resolve references
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities in the passage.
            Entities: {entities_extraction}
            Question: {question_analysis}""",
            context=question_analysis
        )

        # Step 4: Generate solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Execute the required operation based on the question analysis.
                Perform addition, subtraction, counting, sorting, or comparison as needed.
                Entities: {entities_extraction}
                Question: {question_analysis}
                References: {reference_resolution}""",
                context=reference_resolution
            ),
            self.generate(
                instruction=f"""Consider alternative interpretations of the question.
                Generate a different solution approach.
                Entities: {entities_extraction}
                Question: {question_analysis}
                References: {reference_resolution}""",
                context=reference_resolution
            )
        )

        # Step 5: Revise solution attempts
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and refine the solution attempt.
                Correct any errors and improve clarity.
                Original Attempt: {attempt}""",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # Step 6: Ensemble to select the best answer
        final_answer = await self.ensemble(
            instruction="""Evaluate and synthesize the refined solutions to select the best answer.
            Consider accuracy, completeness, and adherence to the expected format.""",
            contexts_list=revised_solutions
        )

        # Step 7: Iterative refinement if needed
        for _ in range(3):  # Allow up to 3 iterations
            validation = await self.generate(
                instruction=f"""Validate the final answer.
                Check for ambiguity, missing information, or format issues.
                Final Answer: {final_answer}""",
                context=final_answer
            )
            if "error" in validation.lower() or "ambiguous" in validation.lower():
                final_answer = await self.revise(
                    instruction=f"""Address issues identified in validation.
                    Issues: {validation}
                    Original Answer: {final_answer}""",
                    context=final_answer
                )
            else:
                break

        return final_answer