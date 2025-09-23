# Workflow ID: drop_176_0
# Benchmark: drop
# Data Indices: [185, 343]

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
        import re

        # Step 1: Extract all named entities, numbers, and relationships
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list:
            - Entities: [names, roles, locations]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=""
        )

        # Step 2: Classify the question type
        question_classification = await self.generate(
            instruction=f"""Classify the question type based on the following categories:
            - Arithmetic (e.g., addition, subtraction)
            - Counting (e.g., how many times)
            - Comparison (e.g., which is greater)
            - Span Extraction (e.g., who did, what was)
            - Multi-step (requires combining multiple operations)
            
            Passage entities and numbers:
            {entities_and_numbers}
            
            Question:
            [QUESTION FROM THE PROBLEM TEXT]
            
            Provide the classification and reasoning.""",
            context=entities_and_numbers
        )

        # Step 3: Parallel processing based on classification
        if "arithmetic" in question_classification.lower():
            # Identify operation and operands
            operation_details = await self.generate(
                instruction=f"""Identify the arithmetic operation and operands:
                - Operation: [addition, subtraction, etc.]
                - Operands: [numbers involved]
                
                Passage entities and numbers:
                {entities_and_numbers}
                
                Question:
                [QUESTION FROM THE PROBLEM TEXT]""",
                context=question_classification
            )
            
            # Extract operands and perform operation
            operands = re.findall(r'\d+', operation_details)
            operands = list(map(int, operands))
            if "addition" in operation_details.lower():
                result = sum(operands)
            elif "subtraction" in operation_details.lower():
                result = operands[0] - operands[1]
            else:
                result = "Unsupported operation"

        elif "counting" in question_classification.lower():
            # Count relevant instances
            count_result = await self.generate(
                instruction=f"""Count the number of relevant instances:
                - What to count: [specific entity or event]
                
                Passage entities and numbers:
                {entities_and_numbers}
                
                Question:
                [QUESTION FROM THE PROBLEM TEXT]""",
                context=question_classification
            )
            result = re.search(r'\d+', count_result).group()

        elif "comparison" in question_classification.lower():
            # Compare values
            comparison_details = await self.generate(
                instruction=f"""Identify the values to compare and the comparison type:
                - Values: [numbers or entities to compare]
                - Type: [greater, less, equal]
                
                Passage entities and numbers:
                {entities_and_numbers}
                
                Question:
                [QUESTION FROM THE PROBLEM TEXT]""",
                context=question_classification
            )
            values = re.findall(r'\d+', comparison_details)
            values = list(map(int, values))
            if "greater" in comparison_details.lower():
                result = max(values)
            elif "less" in comparison_details.lower():
                result = min(values)
            else:
                result = "Unsupported comparison"

        elif "span extraction" in question_classification.lower():
            # Extract exact text span
            span_result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                - Ensure the span matches the passage exactly
                
                Passage:
                [PASSAGE FROM THE PROBLEM TEXT]
                
                Question:
                [QUESTION FROM THE PROBLEM TEXT]""",
                context=question_classification
            )
            result = span_result.strip()

        else:
            # Default approach for multi-step or ambiguous questions
            result = await self.generate(
                instruction=f"""Provide a comprehensive answer by combining multiple steps:
                - Identify all required operations
                - Execute them in sequence
                
                Passage entities and numbers:
                {entities_and_numbers}
                
                Question:
                [QUESTION FROM THE PROBLEM TEXT]""",
                context=question_classification
            )

        # Step 4: Validate and refine the result
        validated_result = await self.revise(
            instruction=f"""Validate the result:
            - Check for logical consistency
            - Resolve any ambiguities
            - Ensure the format matches the expected answer type
            
            Result:
            {result}""",
            context=result
        )

        # Final synthesis
        final_answer = await self.ensemble(
            instruction="Synthesize all insights into the final answer.",
            contexts_list=[result, validated_result]
        )

        return final_answer