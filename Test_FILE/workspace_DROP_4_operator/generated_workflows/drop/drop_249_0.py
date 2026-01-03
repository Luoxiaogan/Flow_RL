# Workflow ID: drop_249_0
# Benchmark: drop
# Data Indices: [339, 443]

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

        # Step 1: Initial Analysis and Entity Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Reference Resolution and Question Classification
        reference_resolution, question_classification = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve references in the question to specific entities in the passage.
                Passage Entities: {entities}
                Question: [Question text]
                Resolve pronouns and partial names to full entities.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Classify the question type based on its phrasing.
                Passage Entities: {entities}
                Question: [Question text]
                Identify if the question is arithmetic, counting, comparison, span extraction, or multi-step.""",
                context=entities
            )
        )

        # Step 3: Conditional Branching Based on Question Type
        if "arithmetic" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Solve the arithmetic problem using the extracted entities.
                Passage Entities: {entities}
                Resolved References: {reference_resolution}
                Perform the necessary arithmetic operations and provide the final answer.""",
                context=f"{entities}

{reference_resolution}"
            )
        elif "counting" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event.
                Passage Entities: {entities}
                Resolved References: {reference_resolution}
                Provide the count as the final answer.""",
                context=f"{entities}

{reference_resolution}"
            )
        elif "comparison" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Compare the specified values or attributes.
                Passage Entities: {entities}
                Resolved References: {reference_resolution}
                Provide the comparison result as the final answer.""",
                context=f"{entities}

{reference_resolution}"
            )
        elif "span extraction" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span matching the question criteria.
                Passage Entities: {entities}
                Resolved References: {reference_resolution}
                Provide the exact text span as the final answer.""",
                context=f"{entities}

{reference_resolution}"
            )
        else:  # Multi-step problems
            intermediate_steps = []
            for step in ["Identify sub-problems", "Solve each sub-problem", "Combine results"]:
                intermediate_result = await self.generate(
                    instruction=f"""{step} for the multi-step problem.
                    Passage Entities: {entities}
                    Resolved References: {reference_resolution}""",
                    context=f"{entities}

{reference_resolution}"
                )
                intermediate_steps.append(intermediate_result)
            
            result = await self.ensemble(
                instruction="Synthesize intermediate results into the final answer.",
                contexts_list=intermediate_steps
            )

        # Step 4: Validation and Refinement
        for i in range(3):
            validation = await self.generate(
                instruction=f"Validate step {i+1} output: {result}",
                context=result
            )
            if "error" in validation.lower():
                result = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=result
                )
            else:
                break

        # Step 5: Final Answer Formatting
        final_answer = await self.generate(
            instruction=f"""Format the final answer appropriately.
            Result: {result}
            Ensure the output matches the expected format (number, date, or exact text span).""",
            context=result
        )

        return final_answer