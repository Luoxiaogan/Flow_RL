# Workflow ID: drop_146_0
# Benchmark: drop
# Data Indices: [386, 279]

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

        # Step 1: Extract entities, numbers, and relationships (Parallel with question classification)
        extract_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        classify_task = self.generate(
            instruction="""Classify the question type based on its phrasing:
            - Counting: 'How many', 'How much'
            - Arithmetic: 'What is the difference', 'How many more'
            - Comparison: 'Which is greater', 'Who had more'
            - Span Extraction: 'Who did', 'What was the name of'""",
            context=""
        )
        extracted_info, question_type = await asyncio.gather(extract_task, classify_task)

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Map question references to specific entities in the passage:
            Passage Entities: {extracted_info}
            Question: {self.problem_text}
            Resolve pronouns and partial names to full entities.""",
            context=extracted_info
        )

        # Step 3: Identify and execute the required operation (Conditional Branching)
        if "counting" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event:
                Passage: {self.problem_text}
                Resolved References: {resolved_references}""",
                context=extracted_info
            )
        elif "arithmetic" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Passage: {self.problem_text}
                Resolved References: {resolved_references}""",
                context=extracted_info
            )
        elif "comparison" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Compare the specified entities or values:
                Passage: {self.problem_text}
                Resolved References: {resolved_references}""",
                context=extracted_info
            )
        elif "span extraction" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage: {self.problem_text}
                Resolved References: {resolved_references}""",
                context=extracted_info
            )
        else:
            operation_result = await self.generate(
                instruction=f"""Use general reasoning to answer the question:
                Passage: {self.problem_text}
                Resolved References: {resolved_references}""",
                context=extracted_info
            )

        # Step 4: Validate and refine the result
        validated_result = await self.revise(
            instruction=f"""Validate the result for accuracy and format:
            Expected formats: number, date, exact text span.
            Result: {operation_result}""",
            context=operation_result
        )

        # Step 5: Handle ambiguity with ensemble synthesis (if needed)
        if "ambiguous" in validated_result.lower():
            interpretations = await asyncio.gather(
                self.generate(instruction="Interpret the result differently...", context=validated_result),
                self.generate(instruction="Consider alternative perspectives...", context=validated_result)
            )
            final_answer = await self.ensemble(
                instruction="Select the most accurate interpretation.",
                contexts_list=interpretations
            )
        else:
            final_answer = validated_result

        return final_answer