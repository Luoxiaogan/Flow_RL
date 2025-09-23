# Workflow ID: mbpp_98_0
# Benchmark: mbpp
# Data Indices: [40]

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

        # Step 1: Extract function name and classify problem type
        function_info = await self.generate(
            instruction="""Extract the function name from the assert statements and classify the problem type (e.g., mathematical computation, list manipulation). 
            Provide structured output:
            - Function Name: [name]
            - Problem Type: [type]""",
            context=""
        )

        # Step 2: Parse natural language description and generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Based on the extracted function name and problem type:
            Function Name: {function_info.split('Function Name: ')[1].split('Problem Type:')[0].strip()}
            Problem Type: {function_info.split('Problem Type: ')[1].strip()}
            
            Parse the natural language description and generate an initial solution. 
            Include necessary imports, proper indentation, and comments explaining the logic.""",
            context=function_info
        )

        # Step 3: Validate initial solution against test cases
        validation_result = await self.generate(
            instruction=f"""Validate the following solution against the provided test cases:
            Solution:
            {initial_solution}
            
            Identify any discrepancies or errors. If valid, confirm with 'PASS'. Otherwise, provide detailed feedback.""",
            context=initial_solution
        )

        # Step 4: Iterative refinement loop
        max_iterations = 3
        refined_solution = initial_solution
        for i in range(max_iterations):
            if "PASS" in validation_result:
                break  # Exit loop if solution passes validation
            
            refined_solution = await self.revise(
                instruction=f"""Improve the solution based on the following feedback:
                Feedback:
                {validation_result}
                
                Ensure the solution passes all test cases and handles edge cases.""",
                context=refined_solution
            )
            
            validation_result = await self.generate(
                instruction=f"""Re-validate the refined solution:
                Refined Solution:
                {refined_solution}""",
                context=refined_solution
            )

        # Step 5: Generate multiple solution candidates in parallel
        candidate_solutions = await asyncio.gather(
            self.generate(instruction="Generate an alternative solution focusing on simplicity.", context=refined_solution),
            self.generate(instruction="Generate an alternative solution focusing on efficiency.", context=refined_solution)
        )

        # Step 6: Ensemble decision-making to select the best solution
        final_solution = await self.ensemble(
            instruction="""Compare the following solutions and select the best one based on correctness, simplicity, and efficiency:
            Solutions:
            - Candidate 1: {candidate_solutions[0]}
            - Candidate 2: {candidate_solutions[1]}""",
            contexts_list=candidate_solutions
        )

        return final_solution