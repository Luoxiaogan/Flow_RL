# Workflow ID: gsm8k_148_0
# Benchmark: gsm8k
# Data Indices: [30, 288]

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

        # Step 1: Problem Decomposition
        decomposition = await self.generate(
            instruction="""Extract all key information from the problem:
            - Numerical values and their units
            - Relationships between entities
            - What is being asked for
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Identify Solution Path
        solution_path = await self.generate(
            instruction=f"""Based on the extracted information:
            {decomposition}
            
            Identify the logical sequence of operations required to solve the problem:
            - List the steps in order
            - Specify the arithmetic operations needed
            - Highlight any dependencies between steps""",
            context=decomposition
        )

        # Step 3: Execute Calculations
        steps = solution_path.split("\n")
        intermediate_results = []
        for i, step in enumerate(steps):
            if "operation" in step.lower():
                calculation = await self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    
                    Show all intermediate results and track units.""",
                    context="\n".join(intermediate_results)
                )
                intermediate_results.append(calculation)

        # Step 4: Validate Intermediate Results
        validation_tasks = [
            self.revise(
                instruction=f"""Validate the following result:
                {result}
                
                Check for consistency, correct units, and logical flow.""",
                context=result
            )
            for result in intermediate_results
        ]
        validations = await asyncio.gather(*validation_tasks)

        # Step 5: Synthesize Final Answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the final answer from the validated results:
            - Ensure the answer is a single numerical value
            - Match the expected format (integer or decimal)""",
            contexts_list=validations
        )

        return final_answer