# Workflow ID: drop_87_0
# Benchmark: drop
# Data Indices: [92, 355]

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

        # Step 1: Extract entities and classify the question
        entity_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Resolve pronouns and partial names to specific entities. Format as a structured list.""",
            context=""
        )
        question_classification = await self.generate(
            instruction="""Classify the question into one of the following categories:
            - Arithmetic: Involves addition, subtraction, multiplication, or division.
            - Counting: Requires counting occurrences of specific events or entities.
            - Comparison: Asks for comparisons like 'greater than' or 'longer than'.
            - Span Extraction: Requires extracting exact text spans.
            - Multi-Step: Combines multiple operations or facts.
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Conditional branching based on classification
        classification = question_classification.lower()
        if "arithmetic" in classification:
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operations using the extracted entities:
                {entity_extraction}
                Show all steps and provide the final answer.""",
                context=entity_extraction
            )
        elif "counting" in classification:
            result = await self.generate(
                instruction=f"""Count the occurrences of the specified entities or events:
                {entity_extraction}
                Provide the count and reasoning.""",
                context=entity_extraction
            )
        elif "comparison" in classification:
            result = await self.generate(
                instruction=f"""Compare the specified values or entities:
                {entity_extraction}
                Determine the relationship and provide the answer.""",
                context=entity_extraction
            )
        elif "span extraction" in classification:
            result = await self.generate(
                instruction=f"""Extract the exact text span from the passage:
                {entity_extraction}
                Ensure the span matches the passage verbatim.""",
                context=entity_extraction
            )
        elif "multi-step" in classification:
            # Hierarchical decomposition for multi-step problems
            sub_problem_1 = await self.generate(
                instruction=f"""Solve the first sub-problem using the extracted entities:
                {entity_extraction}
                Provide the intermediate result.""",
                context=entity_extraction
            )
            sub_problem_2 = await self.generate(
                instruction=f"""Using the result from the first sub-problem ({sub_problem_1}), solve the second sub-problem:
                {entity_extraction}
                Provide the final answer.""",
                context=sub_problem_1
            )
            result = sub_problem_2
        else:
            result = "Unable to classify the question."

        # Step 3: Validate and refine the result
        validated_result = await self.revise(
            instruction=f"""Validate the result against the passage:
            {result}
            Ensure correctness and refine if needed.""",
            context=result
        )

        return validated_result