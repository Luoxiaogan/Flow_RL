# Workflow ID: drop_79_0
# Benchmark: drop
# Data Indices: [203, 310]

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
        
        # Step 1: Initial Analysis - Extract Entities and Numbers
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )
        
        refined_analysis = await self.revise(
            instruction="Improve the clarity and completeness of the extracted information.",
            context=initial_analysis
        )
        
        # Step 2: Reference Resolution
        reference_resolution = await self.generate(
            instruction=f"""Map pronouns and partial names to specific entities:
            Extracted Information: {refined_analysis}
            Ensure all references are correctly resolved.""",
            context=refined_analysis
        )
        
        resolved_references = await self.revise(
            instruction="Ensure all references are correctly resolved and complete.",
            context=reference_resolution
        )
        
        # Step 3: Operation Identification
        operation_identification = await self.generate(
            instruction=f"""Identify the type of operation required:
            Extracted Information: {resolved_references}
            Determine if the question requires addition, subtraction, counting, comparison, or span extraction.""",
            context=resolved_references
        )
        
        refined_operation = await self.revise(
            instruction="Validate and refine the identified operation.",
            context=operation_identification
        )
        
        # Step 4: Execution and Validation
        execution_attempt = await self.generate(
            instruction=f"""Perform the identified operation and compute the answer:
            Operation: {refined_operation}
            Ensure the answer matches the expected format and validate its correctness.""",
            context=refined_operation
        )
        
        validated_answer = await self.revise(
            instruction="Ensure the answer matches the expected format and validate its correctness.",
            context=execution_attempt
        )
        
        # Step 5: Ensemble Synthesis (if multiple approaches)
        alternative_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Alternative Approach 1:
                Extracted Information: {resolved_references}
                Operation: {refined_operation}
                Compute the answer differently.""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Alternative Approach 2:
                Extracted Information: {resolved_references}
                Operation: {refined_operation}
                Compute the answer differently.""",
                context=resolved_references
            )
        )
        
        final_answer = await self.ensemble(
            instruction="Synthesize the results to select the best answer.",
            contexts_list=[validated_answer] + alternative_approaches
        )
        
        return final_answer