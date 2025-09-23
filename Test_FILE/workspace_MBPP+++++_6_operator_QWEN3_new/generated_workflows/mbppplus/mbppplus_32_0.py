# Workflow ID: mbppplus_32_0
# Benchmark: mbppplus
# Data Indices: [280, 253]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Classify problem type and extract key constraints
        classification = await self.generate(
            instruction="""Analyze the problem and classify it:
            1. Identify the primary domain: mathematical, algorithmic, data structure, string manipulation, or logical.
            2. Extract explicit and implicit constraints from function signature and test cases.
            3. Suggest relevant Python modules or built-in functions that might be applicable.
            4. Predict potential edge cases (empty inputs, single elements, duplicates, boundaries).
            5. Determine if order preservation, mutability, or type consistency is required.
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Generate multiple solution hypotheses in parallel
        hypothesis_instructions = [
            """Based on the problem and classification, generate a Python function implementation.
            Focus on a literal interpretation of test cases. Prioritize simplicity and direct mapping.
            Return ONLY the function body as valid Python code, no explanations or markdown.""",
            
            """Based on the problem and classification, generate a Python function implementation.
            Focus on algorithmic efficiency and use of standard library functions (e.g., heapq, itertools).
            Consider if this is a known algorithm or data structure operation.
            Return ONLY the function body as valid Python code, no explanations or markdown.""",
            
            """Based on the problem and classification, generate a Python function implementation.
            Focus on edge case handling and defensive programming. Assume inputs can be malformed.
            Include explicit type checks and fallback behaviors.
            Return ONLY the function body as valid Python code, no explanations or markdown."""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in hypothesis_instructions]
        )

        # Step 3: Validate and refine each hypothesis against test cases
        validated_solutions = []
        for i, hypothesis in enumerate(hypotheses):
            current_code = hypothesis
            for attempt in range(3):  # Allow up to 3 revision attempts
                try:
                    # Test the code
                    test_result = await self.programmer(
                        instruction="""Execute this code against the provided test cases.
                        Return 'PASS' if all tests pass, or 'FAIL: <reason>' if any fail.
                        Do not modify the code - only report pass/fail status.""",
                        context=current_code
                    )
                    
                    if "PASS" in test_result:
                        validated_solutions.append(current_code)
                        break
                    else:
                        # Revise based on failure
                        current_code = await self.revise(
                            instruction=f"""The following code failed testing: {test_result}
                            Revise the implementation to fix the issue while preserving core logic.
                            Maintain the exact function signature. Return ONLY the revised function body.""",
                            context=current_code
                        )
                except Exception as e:
                    # If execution fails, attempt revision
                    current_code = await self.revise(
                        instruction=f"""Code execution failed with error: {str(e)}
                        Revise the implementation to fix syntax or runtime errors.
                        Return ONLY the revised function body.""",
                        context=current_code
                    )
            else:
                # If all attempts fail, still include for ensemble consideration
                validated_solutions.append(current_code)

        # Step 4: Generate edge cases and perform robustness validation
        edge_cases = await self.generate(
            instruction="""Based on the problem classification and function signature,
            generate 5 comprehensive edge case test scenarios not shown in examples.
            Include: empty inputs, single elements, extreme values, type boundaries, and malformed inputs.
            Format each as a Python assert statement that should pass if the solution is robust.
            Return only the assert statements, one per line.""",
            context=classification
        )

        # Test each validated solution against edge cases
        robust_solutions = []
        for solution in validated_solutions:
            edge_test_result = await self.programmer(
                instruction=f"""Test the following code against these edge cases:
                {edge_cases}
                Return 'ROBUST' if all edge cases pass, or 'FRAGILE: <failed cases>' if any fail.
                Do not modify the code - only report status.""",
                context=solution
            )
            
            if "ROBUST" in edge_test_result:
                robust_solutions.append(solution)
            else:
                # Attempt one revision for edge case failures
                revised = await self.revise(
                    instruction=f"""The solution failed edge case testing: {edge_test_result}
                    Strengthen the implementation to handle these edge cases while maintaining core functionality.
                    Return ONLY the revised function body.""",
                    context=solution
                )
                robust_solutions.append(revised)

        # Step 5: Ensemble - select best solution
        if len(robust_solutions) > 1:
            final_solution = await self.ensemble(
                instruction="""Select the best solution from the candidates below.
                Criteria:
                1. Correctness (passes all test cases)
                2. Robustness (handles edge cases)
                3. Simplicity and readability
                4. Efficiency and appropriate use of standard libraries
                5. Adherence to problem constraints
                Return ONLY the selected function body, no explanations.""",
                contexts_list=robust_solutions
            )
        elif len(robust_solutions) == 1:
            final_solution = robust_solutions[0]
        else:
            # Fallback: return first hypothesis if all else fails
            final_solution = hypotheses[0] if hypotheses else "def function(): return None"

        # Step 6: Final cleanup and formatting
        cleaned_solution = await self.revise(
            instruction="""Ensure the code meets all requirements:
            1. Exact function signature as specified in problem
            2. Proper imports if needed
            3. Clean, readable formatting
            4. No extra text or explanations - only valid Python code
            5. Handle edge cases appropriately
            Return ONLY the cleaned function implementation.""",
            context=final_solution
        )

        return cleaned_solution