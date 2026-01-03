# Workflow ID: drop_139_0
# Benchmark: drop
# Data Indices: [209, 2]

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

        # Step 1: Entity Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Problem Classification
        classification = await self.generate(
            instruction=f"""Classify this problem based on the question:
            Entities and numbers: {entities}
            
            Identify:
            - Problem type (arithmetic, counting, comparison, span extraction, multi-step)
            - Required operations (counting, addition, subtraction, etc.)
            - Expected answer format (number, date, text span)""",
            context=entities
        )

        # Step 3: Operation Execution
        if "counting" in classification.lower():
            # Count all instances of a specific event
            count_result = await self.generate(
                instruction=f"""Count all instances of the specified event:
                Entities and numbers: {entities}
                Problem classification: {classification}""",
                context=entities
            )
            result = count_result
        elif "arithmetic" in classification.lower():
            # Perform arithmetic calculations
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operations:
                Entities and numbers: {entities}
                Problem classification: {classification}""",
                context=entities
            )
            result = arithmetic_result
        elif "comparison" in classification.lower():
            # Compare two or more values
            comparison_result = await self.generate(
                instruction=f"""Compare the specified values:
                Entities and numbers: {entities}
                Problem classification: {classification}""",
                context=entities
            )
            result = comparison_result
        elif "span extraction" in classification.lower():
            # Extract exact text span
            span_result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Entities and numbers: {entities}
                Problem classification: {classification}""",
                context=entities
            )
            result = span_result
        else:
            # Default approach for multi-step problems
            multi_step_result = await self.generate(
                instruction=f"""Solve the multi-step problem:
                Entities and numbers: {entities}
                Problem classification: {classification}""",
                context=entities
            )
            result = multi_step_result

        # Step 4: Validation and Correction
        validated_result = await self.revise(
            instruction=f"""Validate the result and correct any errors:
            Result: {result}
            Entities and numbers: {entities}
            Problem classification: {classification}""",
            context=result
        )

        # Step 5: Final Synthesis
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the final answer:
            Validated result: {validated_result}
            Entities and numbers: {entities}
            Problem classification: {classification}""",
            contexts_list=[validated_result, entities, classification]
        )

        return final_answer