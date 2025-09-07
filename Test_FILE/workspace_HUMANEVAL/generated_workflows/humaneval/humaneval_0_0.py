# Workflow ID: humaneval_0_0
# Benchmark: humaneval
# Data Indices: [0]

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
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        """
        import asyncio

        # Step 1: Extract function details (name, parameters, docstring)
        extract_instruction = """
        Extract the function name, parameters, and docstring from the problem text. 
        Ensure the function name matches the ENTRY POINT exactly. 
        Include all examples and edge cases mentioned in the docstring.
        """
        extracted_details = await self.generate(instruction=extract_instruction, context=self.problem_text)

        # Step 2: Summarize docstring examples to identify patterns and edge cases
        summarize_instruction = """
        Analyze the docstring examples to identify patterns, edge cases, and constraints. 
        Focus on what the function should do in different scenarios and any special conditions mentioned.
        """
        summarized_examples = await self.summarize(instruction=summarize_instruction, context=extracted_details)

        # Step 3: Generate initial Python code
        generate_code_instruction = f"""
        Based on the extracted function details and summarized examples, generate a Python function.
        Ensure the function name matches the ENTRY POINT exactly.
        Handle all edge cases and adhere to the examples provided in the docstring.
        Return types must match the examples precisely (e.g., int vs float).
        Do not over-engineer; implement exactly what is specified.
        
        Extracted Details: {extracted_details}
        Summarized Examples: {summarized_examples}
        """
        initial_code = await self.generate(instruction=generate_code_instruction, context=self.problem_text)

        # Step 4: Refine the generated code
        refine_instruction = """
        Review the generated code to ensure it adheres to the requirements:
        - Function name matches the ENTRY POINT exactly
        - All examples and edge cases are handled
        - Return types match the examples precisely
        - No over-engineering or unnecessary complexity
        If any issues are found, refine the code accordingly.
        """
        refined_code = await self.revise(instruction=refine_instruction, context=initial_code)

        # Step 5 (Optional): Ensemble evaluation if multiple approaches are generated
        ensemble_instruction = """
        Compare multiple candidate solutions and select the best one based on:
        - Correctness (matches all examples and edge cases)
        - Simplicity (no unnecessary complexity)
        - Adherence to requirements (function name, return types, etc.)
        """
        candidate_solutions = [refined_code]  # Add more candidates if generated
        final_code = await self.ensemble(instruction=ensemble_instruction, contexts=candidate_solutions)

        return final_code