# Workflow ID: drop_215_0
# Benchmark: drop
# Data Indices: [471, 325]

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
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: Names of people, places, teams, etc.
            - Numbers: Quantities, scores, dates, etc.
            - Relationships: How entities and numbers are connected
            Format as a structured list.""",
            context=""
        )

        # Step 2: Reference Resolution - Map pronouns and partial names
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the passage:
            Passage: {self.problem_text}
            Entities: {initial_analysis}
            
            Map each pronoun or partial name to a specific entity based on context.""",
            context=initial_analysis
        )

        # Step 3: Operation Identification - Classify the question type
        operation_identification = await self.generate(
            instruction=f"""Classify the question type and identify required operations:
            Question: [Extract question from problem]
            Entities: {resolved_references}
            
            Possible operations:
            - Counting: Tally occurrences of specific entities or events
            - Arithmetic: Add, subtract, or compare numbers
            - Comparison: Compare attributes like size, time, or quantity
            - Span Extraction: Find exact text spans matching criteria
            
            Provide classification and detailed reasoning.""",
            context=resolved_references
        )

        # Step 4: Parallel Execution - Perform identified operations
        # Extract operation details from classification
        execution_tasks = []
        if "counting" in operation_identification.lower():
            execution_tasks.append(
                self.generate(
                    instruction=f"""Count occurrences of the specified entity or event:
                    Question: [Extract question from problem]
                    Entities: {resolved_references}
                    
                    Provide the count and reasoning.""",
                    context=resolved_references
                )
            )
        if "arithmetic" in operation_identification.lower():
            execution_tasks.append(
                self.generate(
                    instruction=f"""Perform the required arithmetic operation:
                    Question: [Extract question from problem]
                    Entities: {resolved_references}
                    
                    Show all steps and provide the final result.""",
                    context=resolved_references
                )
            )
        if "comparison" in operation_identification.lower():
            execution_tasks.append(
                self.generate(
                    instruction=f"""Compare the specified attributes:
                    Question: [Extract question from problem]
                    Entities: {resolved_references}
                    
                    Provide the comparison result and reasoning.""",
                    context=resolved_references
                )
            )
        if "span extraction" in operation_identification.lower():
            execution_tasks.append(
                self.generate(
                    instruction=f"""Extract the exact text span matching the criteria:
                    Question: [Extract question from problem]
                    Passage: {self.problem_text}
                    
                    Provide the span and reasoning.""",
                    context=resolved_references
                )
            )

        # Execute tasks in parallel
        execution_results = await asyncio.gather(*execution_tasks)

        # Step 5: Ensemble - Synthesize results into final answer
        final_answer = await self.ensemble(
            instruction="""Synthesize all results into a single answer:
            - Select the most accurate result
            - Ensure the answer matches the expected format (number, date, text span)
            - Provide reasoning for the selection.""",
            contexts_list=execution_results
        )

        return final_answer