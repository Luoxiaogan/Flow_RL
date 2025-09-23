# Workflow ID: drop_147_0
# Benchmark: drop
# Data Indices: [118, 345]

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
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and their relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Step 2: Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Entities: {entities}
            
            Identify and map all references to their corresponding entities.""",
            context=entities
        )
        
        # Step 3: Classify the question type
        question_type = await self.generate(
            instruction=f"""Classify the question type based on its phrasing:
            Entities and References: {resolved_references}
            
            Categories:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Greater/longer, more, first/last, etc.
            - Span Extraction: Who did, what was the name of, when did, etc.
            - Multi-step: Questions requiring chaining multiple operations or facts
            
            Provide the classification and reasoning.""",
            context=resolved_references
        )
        
        # Step 4: Execute operations based on classification
        if "arithmetic" in question_type.lower():
            operations = ["addition", "subtraction"]
        elif "counting" in question_type.lower():
            operations = ["count occurrences", "count unique entities"]
        elif "comparison" in question_type.lower():
            operations = ["greater than", "less than", "first occurrence", "last occurrence"]
        elif "span extraction" in question_type.lower():
            operations = ["extract exact text span"]
        else:
            operations = ["multi-step reasoning"]

        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Perform {op} based on the passage and question:
                Entities and References: {resolved_references}
                
                Provide the result of the operation.""",
                context=resolved_references
            ) for op in operations]
        )
        
        # Step 5: Ensemble results if multiple operations were performed
        if len(operation_results) > 1:
            final_result = await self.ensemble(
                instruction="Synthesize results from multiple operations into a single coherent answer.",
                contexts_list=operation_results
            )
        else:
            final_result = operation_results[0]
        
        # Step 6: Refine and format the final answer
        refined_answer = await self.revise(
            instruction=f"""Refine and format the final answer:
            Ensure it matches the expected format (number, date, or exact text span).
            Final Result: {final_result}""",
            context=final_result
        )
        
        return refined_answer