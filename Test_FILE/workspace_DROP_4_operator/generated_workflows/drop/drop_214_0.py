# Workflow ID: drop_214_0
# Benchmark: drop
# Data Indices: [498, 207]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage:
            - Entities: Named people, places, organizations, etc.
            - Numbers: All numerical values and what they represent
            - Relationships: How entities and numbers are connected
            Provide this as a structured list.""",
            context=""
        )

        # Step 2: Question Classification - Determine the type of question
        question_type = await self.generate(
            instruction=f"""Classify the question based on the following:
            Passage Analysis: {initial_analysis}
            Question: [QUESTION]
            
            Categories:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many instances, etc.
            - Comparison: Which is greater, which came first, etc.
            - Span Extraction: Who did, what was the name of, etc.
            - Multi-step: Combines multiple operations
            
            Provide the classification and reasoning.""",
            context=initial_analysis
        )

        # Step 3: Reference Resolution - Map question references to passage entities
        resolved_references = await self.generate(
            instruction=f"""Resolve all references in the question to specific entities in the passage:
            Passage Analysis: {initial_analysis}
            Question: [QUESTION]
            
            Resolve pronouns, partial names, and implicit references.
            Provide mappings as a dictionary: {{reference: entity}}.""",
            context=question_type
        )

        # Step 4: Operation Identification - Determine required operations
        operations = await self.generate(
            instruction=f"""Identify the required operation(s) based on the question type:
            Passage Analysis: {initial_analysis}
            Question Type: {question_type}
            Resolved References: {resolved_references}
            
            Examples:
            - 'How many more' → Subtraction
            - 'What is the difference' → Subtraction
            - 'How many times' → Counting
            - 'Which is greater' → Comparison
            
            Provide the operation(s) and reasoning.""",
            context=resolved_references
        )

        # Step 5: Execution and Validation - Perform operations and validate results
        raw_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Execute the identified operation(s):
                Passage Analysis: {initial_analysis}
                Operations: {operations}
                
                Show all steps and calculations.""",
                context=operations
            ),
            self.generate(
                instruction=f"""Validate the execution results:
                Passage Analysis: {initial_analysis}
                Operations: {operations}
                
                Check for errors, inconsistencies, or missing data.""",
                context=operations
            )
        )
        validated_answer = await self.revise(
            instruction="Refine the raw answer based on validation feedback.",
            context="\n".join(raw_answers)
        )

        # Step 6: Answer Formatting - Format the final answer
        formatted_answer = await self.ensemble(
            instruction=f"""Format the final answer based on the expected output:
            Validated Answer: {validated_answer}
            
            Expected formats:
            - Number: Plain integer or decimal
            - Date: YYYY-MM-DD or similar
            - Text Span: Exact match from the passage
            
            Select the best format and provide the final answer.""",
            contexts_list=[validated_answer]
        )

        return formatted_answer