# Workflow ID: mbpp_101_0
# Benchmark: mbpp
# Data Indices: [121]

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

        # Stage 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract the function name from the assert statements.
            - Classify the problem type (e.g., list operations, mathematical computations).
            - Identify key requirements, constraints, and expected behaviors.
            Provide a structured summary.""",
            context=""
        )

        # Extract function name using regex
        function_name_match = re.search(r"assert\s+(\w+)\(", self.problem_text)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"

        # Stage 2: Solution Strategy Development
        candidates = await asyncio.gather(
            self.generate(instruction=f"Develop a solution strategy for {function_name} focusing on list operations.", context=analysis),
            self.generate(instruction=f"Develop a solution strategy for {function_name} focusing on mathematical computations.", context=analysis),
            self.generate(instruction=f"Develop a solution strategy for {function_name} focusing on string manipulations.", context=analysis)
        )
        best_strategy = await self.ensemble(
            instruction="Select the most appropriate solution strategy based on completeness and feasibility.",
            contexts_list=candidates
        )

        # Stage 3: Code Generation and Refinement
        initial_code = await self.generate(
            instruction=f"""Generate Python code for {function_name} based on the selected strategy:
            - Include all necessary imports.
            - Use proper indentation and structure.
            - Ensure the code satisfies the test cases.""",
            context=best_strategy
        )
        refined_code = await self.revise(
            instruction="Refine the code for clarity, efficiency, and correctness. Validate against test cases.",
            context=initial_code
        )

        # Stage 4: Final Validation and Output
        final_output = await self.generate(
            instruction=f"""Format the final output for {function_name}:
            - Ensure the code is complete and executable.
            - Include all test cases for validation.""",
            context=refined_code
        )

        return final_output