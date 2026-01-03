# Workflow ID: drop_99_0
# Benchmark: drop
# Data Indices: [251, 40]

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

        # Phase 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            
            Classify the problem type:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - Are there multiple valid approaches?
            - What's the expected answer format?""",
            context=""
        )

        # Phase 2: Reference Resolution
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Entities: {initial_analysis}
            
            Map each reference to its corresponding entity based on context.""",
            context=initial_analysis
        )

        # Phase 3: Operation Identification and Execution
        operation_plan = await self.generate(
            instruction=f"""Identify the required operation(s) based on the question:
            Entities and References: {resolved_references}
            
            Determine the operation type (addition, subtraction, counting, comparison, etc.)
            and outline the steps needed to compute the answer.""",
            context=resolved_references
        )

        # Execute operations in parallel if multi-step
        operations = re.findall(r"Step \d+: .*", operation_plan)
        if len(operations) > 1:
            results = await asyncio.gather(
                *[self.revise(instruction=f"Execute: {op}", context=operation_plan) for op in operations]
            )
            final_result = await self.ensemble(
                instruction="Combine results from all steps into a single answer.",
                contexts_list=results
            )
        else:
            final_result = await self.revise(
                instruction=f"Execute: {operations[0]}",
                context=operation_plan
            )

        # Phase 4: Validation and Formatting
        validated_answer = await self.generate(
            instruction=f"""Validate the answer against expected format:
            Final Result: {final_result}
            
            Ensure the answer matches the required format (number, date, exact text span).
            Revise if necessary.""",
            context=final_result
        )

        return validated_answer