# Workflow ID: drop_248_0
# Benchmark: drop
# Data Indices: [315, 94]

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

        # Step 1: Initial Extraction
        initial_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and their relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Teams: [names and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Parallel Analysis
        reference_resolution = self.generate(
            instruction=f"""Resolve all pronouns and partial references in the question to specific entities in the passage. 
            Use the following extracted information:
            {initial_extraction}""",
            context=initial_extraction
        )

        operation_identification = self.generate(
            instruction=f"""Analyze the question phrasing to determine the required operation(s). 
            Include reasoning steps. Use the following extracted information:
            {initial_extraction}""",
            context=initial_extraction
        )

        # Run parallel branches
        resolved_references, identified_operations = await asyncio.gather(reference_resolution, operation_identification)

        # Step 3: Synthesis
        synthesis = await self.ensemble(
            instruction="""Combine the resolved references and identified operations into a unified problem-solving strategy. 
            Ensure all required information is accounted for.""",
            contexts_list=[resolved_references, identified_operations]
        )

        # Step 4: Execution and Validation
        execution = await self.generate(
            instruction=f"""Execute the identified operation(s) using the extracted information. 
            Validate the result against the expected format. Unified strategy:
            {synthesis}""",
            context=synthesis
        )

        # Step 5: Feedback Loop
        validation = await self.generate(
            instruction=f"""Validate the execution result. Check if the answer matches the expected format. 
            Execution result:
            {execution}""",
            context=execution
        )

        if "error" in validation.lower():
            refined_result = await self.revise(
                instruction=f"""Refine the extraction or operation execution based on validation feedback. 
                Feedback:
                {validation}""",
                context=execution
            )
            return refined_result
        else:
            return execution