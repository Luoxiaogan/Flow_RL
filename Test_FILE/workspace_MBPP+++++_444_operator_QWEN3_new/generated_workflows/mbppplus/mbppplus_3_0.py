# Workflow ID: mbppplus_3_0
# Benchmark: mbppplus
# Data Indices: [58, 369, 17]

import asyncio

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

        # Step 1: Deep problem analysis and classification
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Your analysis must include:
            1. Problem Type Classification: Is this problem trivial (single operation), moderate (requires loops/conditionals), or complex (multiple edge cases, nested logic)?
            2. Input/Output Specification: What are the exact input types and expected output types? Are there any implicit type conversions?
            3. Edge Case Identification: What edge cases must be handled? (empty inputs, single elements, duplicates, negative numbers, boundary values)
            4. Order Sensitivity: Does the solution need to preserve input order, or is order irrelevant?
            5. Performance Considerations: Are there efficiency constraints? Should we prioritize readability or speed?
            6. Reference Style Analysis: If a reference solution is provided, what programming patterns does it use? (loops, comprehensions, built-in functions)
            7. Test Case Inference: Beyond the shown test cases, what additional test cases would thoroughly validate the solution?
            Structure your response clearly with numbered sections for each point above.""",
            context=""
        )

        # Step 2: Generate multiple solution candidates in parallel
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate a solution that closely follows the reference solution's style and approach.
                Problem Analysis Context: {problem_analysis}
                Requirements:
                - Use similar control structures (loops, conditionals) as reference
                - Maintain the same level of explicitness
                - Handle all edge cases identified in the analysis
                - Return the exact expected data type
                - Include defensive programming for unexpected inputs
                Output ONLY the function implementation with necessary imports, nothing else.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate an optimized, Pythonic solution using built-in functions and data structures.
                Problem Analysis Context: {problem_analysis}
                Requirements:
                - Use collections.Counter, set operations, or itertools if appropriate
                - Prioritize readability and conciseness
                - Handle all edge cases identified in the analysis
                - Return the exact expected data type
                - Include necessary imports at the top
                Output ONLY the function implementation with necessary imports, nothing else.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a defensively programmed solution that explicitly handles every possible edge case.
                Problem Analysis Context: {problem_analysis}
                Requirements:
                - Include explicit checks for empty inputs, type validation, boundary conditions
                - Use verbose but unambiguous logic
                - Prioritize robustness over elegance
                - Return the exact expected data type
                - Include comprehensive error handling
                Output ONLY the function implementation with necessary imports, nothing else.""",
                context=problem_analysis
            )
        ]
        
        candidate_solutions = await asyncio.gather(*candidate_tasks)

        # Step 3: Ensemble synthesis - select and refine the best solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the candidates provided. Your task:
            1. Compare all candidate solutions against the problem requirements and edge cases identified in the analysis.
            2. Evaluate each solution on: correctness, edge case handling, code clarity, and adherence to expected output format.
            3. Select the solution that best balances robustness and elegance, or create a hybrid that combines the strongest elements.
            4. If no solution perfectly handles all edge cases, revise the selected solution to address the gaps.
            5. Ensure the final output matches EXACTLY the required format: only the function implementation with necessary imports.
            Do NOT include any explanations, markdown, or additional text - only the pure Python function code.""",
            contexts_list=candidate_solutions
        )

        # Step 4: Validation loop - generate test cases and verify solution
        for iteration in range(3):  # Maximum 3 refinement iterations
            validation_analysis = await self.generate(
                instruction=f"""Generate comprehensive test cases to validate the solution. Include:
                1. All edge cases mentioned in the original problem analysis
                2. Additional boundary cases not shown in original examples
                3. Type variation tests (if applicable)
                4. Performance stress tests (large inputs, if relevant)
                Then, mentally execute the current solution against these test cases.
                If you find any failures or weaknesses, describe them specifically.
                If the solution passes all tests, respond with 'VALIDATED'.
                Current solution: {final_solution}""",
                context=final_solution
            )

            if "VALIDATED" in validation_analysis:
                break
            else:
                # Revise solution based on validation failures
                final_solution = await self.revise(
                    instruction=f"""Revise the solution to fix the issues identified in validation.
                    Validation Feedback: {validation_analysis}
                    Requirements:
                    - Address all specific failures mentioned
                    - Maintain correct function signature and return type
                    - Preserve working functionality while fixing bugs
                    - Output ONLY the revised function implementation
                    Do NOT include any explanations or additional text.""",
                    context=final_solution
                )

        return final_solution