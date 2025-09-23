# Workflow ID: drop_244_0
# Benchmark: drop
# Data Indices: [199, 75]

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

        # Step 1: Parallel Fork - Extract entities, resolve references, classify problem
        entities, references, classification = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities, numbers, and relationships:
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ),
            self.generate(
                instruction="""Resolve all pronouns and partial references to specific entities:
                Provide mapping of references to entities.""",
                context=""
            ),
            self.generate(
                instruction="""Classify this problem:
                1. Is it numerical, logical, or textual?
                2. Does it require exact calculation or estimation?
                3. What operation(s) are needed (addition, subtraction, counting, comparison)?
                4. What is the expected answer format?""",
                context=""
            )
        )

        # Step 2: Process - Determine required operation(s)
        operation_plan = await self.generate(
            instruction=f"""Based on the following information:
            Entities: {entities}
            References: {references}
            Classification: {classification}
            
            Plan the required operation(s) step-by-step.""",
            context=f"{entities}\n{references}\n{classification}"
        )

        # Step 3: Execute - Perform the operation(s)
        execution_result = await self.generate(
            instruction=f"""Execute the planned operations:
            {operation_plan}
            
            Show all steps and intermediate results.""",
            context=operation_plan
        )

        # Step 4: Validate - Check for errors and refine
        validation = await self.revise(
            instruction="""Validate the result:
            - Are all steps logically consistent?
            - Are there any missing details?
            - Does the answer match the expected format?""",
            context=execution_result
        )

        # Step 5: Feedback Loop - Refine if necessary
        if "error" in validation.lower():
            refined_result = await self.revise(
                instruction=f"Fix issues: {validation}",
                context=execution_result
            )
        else:
            refined_result = execution_result

        # Step 6: Merge - Synthesize into final answer
        final_answer = await self.summarize(
            instruction="""Condense the result into the final answer:
            - Ensure it matches the expected format.
            - Include only the essential information.""",
            context=refined_result
        )

        return final_answer