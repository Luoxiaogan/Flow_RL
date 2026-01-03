# Workflow ID: drop_226_0
# Benchmark: drop
# Data Indices: [47, 236]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and their relationships from the passage. 
            Classify the problem type based on the question (e.g., arithmetic, counting, comparison, span extraction). 
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Parallel Processing - Resolve references and perform operations
        reference_resolution = self.generate(
            instruction=f"""Resolve all references in the question to specific entities in the passage. 
            Use the following analysis as context: {initial_analysis}. Ensure pronouns and partial names are correctly mapped.""",
            context=initial_analysis
        )
        operation_execution = self.generate(
            instruction=f"""Identify and execute the required operation(s) based on the problem type. 
            Use the following analysis as context: {initial_analysis}. Perform calculations, comparisons, or span extractions as needed.""",
            context=initial_analysis
        )
        resolved_references, executed_operations = await asyncio.gather(reference_resolution, operation_execution)

        # Step 3: Synthesis - Combine results from parallel processes
        synthesis = await self.ensemble(
            instruction="""Synthesize the resolved references and executed operations into a coherent solution. 
            Ensure all parts of the question are addressed and the answer is logically consistent.""",
            contexts_list=[resolved_references, executed_operations]
        )

        # Step 4: Validation - Refine and validate the solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution: {synthesis}. 
                Check if it answers the question fully and adheres to the required format. Identify any errors or omissions.""",
                context=synthesis
            )
            if "error" not in validation.lower():
                break  # Exit loop if no errors
            synthesis = await self.revise(
                instruction=f"""Revise the solution to address the following issues: {validation}. 
                Ensure the final answer is correct and properly formatted.""",
                context=synthesis
            )

        return synthesis