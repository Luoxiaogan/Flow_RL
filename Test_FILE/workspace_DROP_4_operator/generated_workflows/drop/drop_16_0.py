# Workflow ID: drop_16_0
# Benchmark: drop
# Data Indices: [25, 455]

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

        # Step 1: Initial Analysis - Extract entities and classify problem
        analysis_tasks = await asyncio.gather(
            self.generate(
                instruction="""Extract all entities, numbers, and relationships:
                - Entities: Names, roles, locations, teams
                - Numbers: Values and what they represent
                - Relationships: Actions, events, and their connections""",
                context=""
            ),
            self.generate(
                instruction="""Classify the problem type:
                - Arithmetic: Addition, subtraction, comparison
                - Counting: How many times, occurrences
                - Comparison: Greater than, less than, equal to
                - Span Extraction: Exact text spans
                - Multi-Hop: Chaining multiple facts""",
                context=""
            )
        )
        extracted_info, problem_type = analysis_tasks

        # Step 2: Reference Resolution
        resolved_references = await self.revise(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Extracted Info: {extracted_info}
            Problem Type: {problem_type}
            
            Resolve references such as 'he', 'she', 'they', 'the team', etc., to their full names or entities.""",
            context=extracted_info
        )

        # Step 3: Operation Execution
        if "arithmetic" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Extracted Info: {resolved_references}
                Problem Type: {problem_type}
                
                Identify numbers and their relationships, then compute the result.""",
                context=resolved_references
            )
        elif "counting" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event:
                Extracted Info: {resolved_references}
                Problem Type: {problem_type}
                
                Identify the target entity/event and count its occurrences.""",
                context=resolved_references
            )
        elif "comparison" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Compare the specified values or spans:
                Extracted Info: {resolved_references}
                Problem Type: {problem_type}
                
                Identify values/spans and determine the relationship.""",
                context=resolved_references
            )
        elif "span extraction" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span matching the question criteria:
                Extracted Info: {resolved_references}
                Problem Type: {problem_type}
                
                Identify the relevant part of the passage and extract it verbatim.""",
                context=resolved_references
            )
        elif "multi-hop" in problem_type.lower():
            intermediate_steps = await asyncio.gather(
                self.generate(
                    instruction=f"""Identify the first intermediate fact:
                    Extracted Info: {resolved_references}
                    Problem Type: {problem_type}""",
                    context=resolved_references
                ),
                self.generate(
                    instruction=f"""Identify the second intermediate fact:
                    Extracted Info: {resolved_references}
                    Problem Type: {problem_type}""",
                    context=resolved_references
                )
            )
            result = await self.ensemble(
                instruction="Synthesize intermediate facts into a final answer",
                contexts_list=intermediate_steps
            )
        else:
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                Extracted Info: {resolved_references}
                Problem Type: {problem_type}""",
                context=resolved_references
            )

        # Step 4: Final Validation and Formatting
        final_answer = await self.summarize(
            instruction=f"""Condense the solution into the required format:
            Result: {result}
            Problem Type: {problem_type}
            
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            context=result
        )

        return final_answer.strip()