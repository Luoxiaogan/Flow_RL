# Workflow ID: drop_117_0
# Benchmark: drop
# Data Indices: [393, 59]

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

        # Step 1: Extract all entities, numbers, and relationships
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Classify the question type
        question_type = await self.generate(
            instruction=f"""Classify the question type based on the following:
            Passage: {self.problem_text}
            Question: {self.problem_text.split('**QUESTION:**')[1].split('**ANSWER:**')[0]}
            
            Categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (which is greater, longer, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            - Multi-step (requires chaining multiple operations or facts)
            
            Provide classification and reasoning.""",
            context=entities_and_numbers
        )

        # Step 3: Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve any pronouns or partial names to specific entities from the passage.
            Passage: {self.problem_text}
            Extracted Entities: {entities_and_numbers}
            
            Provide mappings and reasoning.""",
            context=question_type
        )

        # Step 4: Parallel processing based on question type
        if "arithmetic" in question_type.lower():
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation.
                Passage: {self.problem_text}
                Resolved References: {resolved_references}
                
                Show all steps and final result.""",
                context=resolved_references
            )
            final_answer = arithmetic_result
        elif "counting" in question_type.lower():
            counting_result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event.
                Passage: {self.problem_text}
                Resolved References: {resolved_references}
                
                Verify completeness and provide count.""",
                context=resolved_references
            )
            final_answer = counting_result
        elif "comparison" in question_type.lower():
            comparison_result = await self.generate(
                instruction=f"""Compare the specified values or entities.
                Passage: {self.problem_text}
                Resolved References: {resolved_references}
                
                Determine the result and provide reasoning.""",
                context=resolved_references
            )
            final_answer = comparison_result
        elif "span extraction" in question_type.lower():
            span_extraction_result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question.
                Passage: {self.problem_text}
                Resolved References: {resolved_references}
                
                Ensure exact match and provide span.""",
                context=resolved_references
            )
            final_answer = span_extraction_result
        else:  # Multi-step reasoning
            steps = await self.generate(
                instruction=f"""Break down the multi-step reasoning process.
                Passage: {self.problem_text}
                Resolved References: {resolved_references}
                
                List each step and its result.""",
                context=resolved_references
            )
            final_answer = await self.generate(
                instruction=f"""Synthesize the results from each step into a final answer.
                Steps: {steps}""",
                context=steps
            )

        # Step 5: Validate and refine the final answer
        validated_answer = await self.revise(
            instruction=f"""Validate the final answer for accuracy and completeness.
            Final Answer: {final_answer}
            
            Provide feedback and refine if necessary.""",
            context=final_answer
        )

        return validated_answer