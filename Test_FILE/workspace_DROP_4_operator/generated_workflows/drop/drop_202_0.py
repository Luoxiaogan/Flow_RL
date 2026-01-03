# Workflow ID: drop_202_0
# Benchmark: drop
# Data Indices: [169, 293]

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

        # Step 1: Parallel extraction of entities, numbers, and actions
        entities_task = self.generate(
            instruction="""Extract all named entities (people, places, teams, etc.) 
            and their roles/relationships from the passage. Format as a structured list.""",
            context=""
        )
        numbers_task = self.generate(
            instruction="""Extract all numerical values and their contextual meanings 
            (e.g., scores, distances, counts) from the passage. Format as a structured list.""",
            context=""
        )
        actions_task = self.generate(
            instruction="""Identify all actions/events described in the passage 
            and their participants/timing. Format as a structured list.""",
            context=""
        )

        # Gather results
        entities, numbers, actions = await asyncio.gather(entities_task, numbers_task, actions_task)

        # Step 2: Merge extracted information into a unified context
        merged_context = await self.generate(
            instruction=f"""Combine the following information into a unified context:
            Entities: {entities}
            Numbers: {numbers}
            Actions: {actions}
            
            Ensure all references are clear and relationships are preserved.""",
            context=f"{entities}\n{numbers}\n{actions}"
        )

        # Step 3: Classify question type and identify required operations
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine:
            1. The type of operation required (counting, arithmetic, comparison, span extraction, etc.)
            2. Any specific constraints or conditions.
            Provide a structured analysis.""",
            context=merged_context
        )

        # Step 4: Execute the identified operation(s)
        operation_type = "arithmetic" if "difference" in question_analysis.lower() else "counting"
        if operation_type == "arithmetic":
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation using the following data:
                {merged_context}
                
                Show all steps and present the final answer as a number.""",
                context=merged_context
            )
        elif operation_type == "counting":
            result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity/action using:
                {merged_context}
                
                Present the final count as a number.""",
                context=merged_context
            )
        else:
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question using:
                {merged_context}
                
                Ensure the span matches the passage exactly.""",
                context=merged_context
            )

        # Step 5: Validate and format the answer
        validated_answer = await self.revise(
            instruction="""Ensure the answer matches the expected format:
            - Numerical answers should be plain numbers.
            - Text spans should match the passage exactly.
            - Dates should follow standard formats.
            
            Correct any formatting issues.""",
            context=result
        )

        return validated_answer