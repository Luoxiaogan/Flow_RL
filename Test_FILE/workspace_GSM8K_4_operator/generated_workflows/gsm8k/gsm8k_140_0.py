# Workflow ID: gsm8k_140_0
# Benchmark: gsm8k
# Data Indices: [50, 227]

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

        # Step 1: Initial Analysis - Extract key components
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, their units, and relationships:
            - Identify all numbers and what they represent (e.g., cost, quantity, time).
            - Highlight relationships like 'twice as much', 'half of', 'per unit', etc.
            - Note any implicit constraints or assumptions.""",
            context=""
        )

        # Step 2: Plan Generation - Formulate a step-by-step solution plan
        solution_plan = await self.generate(
            instruction=f"""Based on the extracted information:
            {initial_analysis}
            
            Generate a detailed plan to solve the problem:
            - Specify the sequence of operations (addition, subtraction, multiplication, division).
            - Include intermediate steps and expected results.
            - Ensure the plan aligns with the problem's requirements.""",
            context=initial_analysis
        )

        # Step 3: Execution - Perform calculations iteratively
        steps = solution_plan.split("\n")
        intermediate_results = []
        for step in steps:
            if step.strip():  # Skip empty lines
                calculation_result = await self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    
                    Show the result with full precision and include units if applicable.""",
                    context="\n".join(intermediate_results)
                )
                # Validate the calculation
                validated_result = await self.revise(
                    instruction=f"""Verify the correctness of the calculation:
                    {calculation_result}
                    
                    Check for consistency with previous steps and the problem's context.""",
                    context=calculation_result
                )
                intermediate_results.append(validated_result)

        # Step 4: Finalization - Summarize the solution and extract the final answer
        final_summary = await self.summarize(
            instruction="""Condense the solution into a concise format:
            - Focus on the final numerical result.
            - Include relevant units or context.
            - Ensure clarity and precision.""",
            context="\n".join(intermediate_results)
        )

        # Step 5: Ensemble - Compare alternative approaches (if applicable)
        final_answer = await self.ensemble(
            instruction="""Evaluate the summarized solution:
            - Confirm that it addresses the problem's requirements.
            - Select the most accurate and efficient result.""",
            contexts_list=[final_summary]
        )

        return final_answer