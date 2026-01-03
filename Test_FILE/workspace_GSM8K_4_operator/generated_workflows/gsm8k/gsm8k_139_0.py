# Workflow ID: gsm8k_139_0
# Benchmark: gsm8k
# Data Indices: [195, 138]

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
            instruction="""Extract all numerical values, units, and relationships from the problem. 
            Classify the problem type (e.g., sequential operations, rate problems, proportions). 
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Refine Decomposition
        refined_decomposition = await self.revise(
            instruction="Refine the extracted information. Add missing details and correct errors.",
            context=decomposition
        )

        # Step 3: Identify Solution Steps
        solution_steps = await self.generate(
            instruction=f"""Based on the refined decomposition:
            {refined_decomposition}
            
            Identify the sequence of operations required to solve the problem. 
            List each step explicitly, including the operation (+, -, ×, ÷) and the numbers involved.""",
            context=refined_decomposition
        )

        # Step 4: Perform Calculations in Parallel
        steps_list = solution_steps.split("\n")
        calculation_tasks = []
        for step in steps_list:
            task = self.generate(
                instruction=f"""Perform the following calculation:
                {step}
                
                Show the intermediate result with full precision.""",
                context=refined_decomposition
            )
            calculation_tasks.append(task)
        intermediate_results = await asyncio.gather(*calculation_tasks)

        # Step 5: Validate Intermediate Results
        validation_tasks = []
        for i, result in enumerate(intermediate_results):
            task = self.generate(
                instruction=f"""Validate the following intermediate result:
                {result}
                
                Ensure it aligns with the problem's constraints and logical flow.""",
                context=refined_decomposition
            )
            validation_tasks.append(task)
        validations = await asyncio.gather(*validation_tasks)

        # Step 6: Adaptive Refinement
        refined_results = []
        for i, validation in enumerate(validations):
            if "error" in validation.lower():
                refined_result = await self.revise(
                    instruction=f"""Revise the following calculation based on validation feedback:
                    {intermediate_results[i]}
                    
                    Correct any mistakes and recompute.""",
                    context=refined_decomposition
                )
                refined_results.append(refined_result)
            else:
                refined_results.append(intermediate_results[i])

        # Step 7: Synthesize Final Answer
        final_answer = await self.ensemble(
            instruction="Combine all refined results into a single numerical answer. Ensure the final answer is exact.",
            contexts_list=refined_results
        )

        return final_answer