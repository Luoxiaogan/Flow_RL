# Workflow ID: mbpp_85_0
# Benchmark: mbpp
# Data Indices: [67]

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

        # Step 1: Analyze the problem
        analysis = await self.generate(
            instruction="""Extract the following information from the problem:
            - Function name from assert statements
            - Task description in natural language
            - Test cases and their expected outputs
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Write a Python function that:
            - Matches the extracted function name
            - Implements the described task
            - Passes all provided test cases
            Include necessary imports and ensure proper indentation.""",
            context=analysis
        )

        # Step 3: Parallel validation
        async def validate_syntax(code):
            try:
                compile(code, '<string>', 'exec')
                return "Syntax is valid."
            except Exception as e:
                return f"Syntax error: {str(e)}"

        async def validate_test_cases(code):
            try:
                exec(code, globals())
                # Extract test cases from problem text
                test_cases = re.findall(r'assert\s+(.+?)\s+==\s+(.+)', self.problem_text)
                results = []
                for case in test_cases:
                    func_call, expected = case
                    actual = eval(func_call)
                    results.append(actual == eval(expected))
                return "All test cases passed." if all(results) else "Some test cases failed."
            except Exception as e:
                return f"Error during test case validation: {str(e)}"

        async def generate_edge_cases():
            return """Additional test cases:
            - Empty input
            - Input with no matching characters
            - Input with only matching characters"""

        syntax_check, test_validation, edge_cases = await asyncio.gather(
            validate_syntax(initial_solution),
            validate_test_cases(initial_solution),
            generate_edge_cases()
        )

        # Step 4: Iterative refinement
        max_iterations = 3
        refined_solution = initial_solution
        for i in range(max_iterations):
            if "error" in syntax_check.lower() or "failed" in test_validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution to address the following issues:
                    - Syntax: {syntax_check}
                    - Test Validation: {test_validation}
                    - Edge Cases: {edge_cases}""",
                    context=refined_solution
                )
                # Re-validate
                syntax_check, test_validation, _ = await asyncio.gather(
                    validate_syntax(refined_solution),
                    validate_test_cases(refined_solution),
                    asyncio.sleep(0)  # Placeholder for edge case generation
                )
            else:
                break

        # Step 5: Return final solution
        return refined_solution