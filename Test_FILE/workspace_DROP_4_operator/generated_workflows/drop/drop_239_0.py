# Workflow ID: drop_239_0
# Benchmark: drop
# Data Indices: [64, 287]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: [names, places, organizations]
            - Numbers: [values and what they represent]
            - Relationships: [actions, events, and their connections]""",
            context=""
        )

        # Step 2: Problem Classification - Identify the type of problem
        problem_classification = await self.generate(
            instruction=f"""Classify the problem based on the question:
            - Is it numerical, logical, or textual?
            - Does it require arithmetic, counting, or comparison?
            - What is the expected answer format?""",
            context=initial_analysis
        )

        # Step 3: Reference Resolution - Map question terms to entities
        reference_resolution = await self.generate(
            instruction=f"""Resolve references in the question:
            - Map pronouns and partial names to specific entities in the passage
            - Ensure all question terms are linked to exact entities""",
            context=f"{initial_analysis}

{problem_classification}"
        )

        # Step 4: Operation Execution - Perform required operations
        if "arithmetic" in problem_classification.lower():
            operations = await self.generate(
                instruction=f"""Perform arithmetic operations as required:
                - Identify numbers and their relationships
                - Execute addition, subtraction, or other operations
                - Show all steps clearly""",
                context=reference_resolution
            )
        elif "counting" in problem_classification.lower():
            operations = await self.generate(
                instruction=f"""Count instances as required:
                - Identify what needs to be counted
                - Ensure no instances are missed
                - Present the final count""",
                context=reference_resolution
            )
        else:
            operations = await self.generate(
                instruction=f"""Perform comparison or other operations:
                - Identify the elements to compare
                - Determine the relationship (greater, less, equal)
                - Present the result""",
                context=reference_resolution
            )

        # Step 5: Validation and Refinement - Ensure correct format
        validated_result = await self.revise(
            instruction=f"""Validate the answer:
            - Ensure the format matches the expected output
            - Double-check calculations and logic
            - Refine if necessary""",
            context=operations
        )

        # Final Output
        return validated_result