# Workflow ID: drop_130_0
# Benchmark: drop
# Data Indices: [323, 100]

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
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: People, places, organizations
            - Numbers: Counts, percentages, measurements
            - Relationships: Actions, events, dependencies""",
            context=""
        )
        
        # Step 2: Refine extracted entities
        refined_entities = await self.revise(
            instruction="Validate and refine the extracted entities and numbers.",
            context=entities
        )
        
        # Step 3: Analyze question type
        question_analysis = await self.generate(
            instruction="""Classify the question:
            - Is it numerical, logical, or textual?
            - Does it require counting, addition, subtraction, comparison, or span extraction?
            - What is the expected answer format?""",
            context=refined_entities
        )
        
        # Step 4: Conditional branching based on question type
        if "numerical" in question_analysis.lower() and "arithmetic" in question_analysis.lower():
            # Arithmetic operation path
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Use the refined entities: {refined_entities}
                - Show all steps and maintain precision""",
                context=question_analysis
            )
        elif "counting" in question_analysis.lower():
            # Counting path
            result = await self.generate(
                instruction=f"""Count the relevant instances:
                - Use the refined entities: {refined_entities}
                - Ensure no instances are missed""",
                context=question_analysis
            )
        elif "comparison" in question_analysis.lower():
            # Comparison path
            result = await self.generate(
                instruction=f"""Compare the relevant values:
                - Use the refined entities: {refined_entities}
                - Clearly state which is greater/less""",
                context=question_analysis
            )
        else:
            # Span extraction path
            result = await self.generate(
                instruction=f"""Extract the exact text span:
                - Use the refined entities: {refined_entities}
                - Ensure the span matches the passage exactly""",
                context=question_analysis
            )
        
        # Step 5: Validate and refine the result
        validated_result = await self.revise(
            instruction="Ensure the result matches the expected format and is accurate.",
            context=result
        )
        
        # Step 6: Summarize the final answer
        final_answer = await self.summarize(
            instruction="Condense the result into a concise, final answer.",
            context=validated_result
        )
        
        return final_answer