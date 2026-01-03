# Workflow ID: gsm8k_75_0
# Benchmark: gsm8k
# Data Indices: [176, 260]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem.
            Classify the problem type (e.g., rate, proportion, distribution).
            Plan the solution by identifying the sequence of operations needed.""",
            context=""
        )

        # Step 2: Solution Planning
        plan = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Create a detailed step-by-step plan for solving the problem.
            Include intermediate results and their dependencies.""",
            context=analysis
        )

        # Step 3: Parallel Execution and Validation
        steps = plan.split("\n")
        intermediate_results = []
        for step in steps:
            if step.strip():  # Skip empty lines
                result = await self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    
                    Show all intermediate results and ensure numerical accuracy.""",
                    context="\n".join(intermediate_results)
                )
                # Validate the result
                validated_result = await self.revise(
                    instruction=f"""Critique and refine the following result:
                    {result}
                    
                    Ensure logical consistency and numerical accuracy.""",
                    context=result
                )
                intermediate_results.append(validated_result)

        # Step 4: Summarize Results
        summary = await self.summarize(
            instruction="""Condense the intermediate results into a concise summary.
            Focus on the final numerical answer and its derivation.""",
            context="\n".join(intermediate_results)
        )

        # Step 5: Final Output
        final_answer = await self.ensemble(
            instruction="""Synthesize the validated results into the final numerical answer.
            Ensure the answer is exact and matches the problem's requirements.""",
            contexts_list=intermediate_results
        )

        return final_answer