# Workflow ID: mbppplus_110_0
# Benchmark: mbppplus
# Data Indices: [64, 128]

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

        # Phase 1: Problem Classification and Requirement Extraction
        classification = await self.generate(
            instruction="""Analyze the programming problem and classify its core computational archetype. 
            Identify:
            - Primary data structures involved (list, tuple, string, set, etc.)
            - Operation type (transformation, filtering, aggregation, element-wise, etc.)
            - Key constraints (preserve order? handle duplicates? empty inputs? type consistency?)
            - Expected input/output signatures
            - Edge cases likely to be tested (empty, single element, boundary values)
            Output a structured summary that can guide solution strategy selection.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation with Diverse Strategies
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function solution using an IMPERATIVE approach (for loops, index manipulation, explicit conditionals).
                Problem classification: {classification}
                Requirements:
                - Match the exact function signature from the problem
                - Handle all edge cases mentioned in classification
                - Include necessary imports inside the function if needed
                - Return correct data type (list vs tuple vs set)
                - Prioritize readability and explicit handling of edge cases
                Output ONLY the function code, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function solution using a FUNCTIONAL approach (comprehensions, map/filter, built-in functions).
                Problem classification: {classification}
                Requirements:
                - Match the exact function signature from the problem
                - Handle all edge cases mentioned in classification
                - Use functional constructs where natural
                - Return correct data type
                - Prioritize conciseness without sacrificing clarity
                Output ONLY the function code, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function solution using a LIBRARY-ASSISTED approach (consider itertools, functools, or other standard library modules if applicable).
                Problem classification: {classification}
                Requirements:
                - Match the exact function signature
                - Leverage appropriate standard library functions
                - Handle edge cases robustly
                - Return correct data type
                - Only use standard library, no external imports
                Output ONLY the function code, no explanations.""",
                context=""
            )
        )

        # Phase 3: Validation and Iterative Refinement
        validated_candidates = []
        for i, candidate in enumerate(solution_candidates):
            current_candidate = candidate
            for attempt in range(3):  # Max 3 revision attempts
                try:
                    # Validate syntax and basic semantics
                    validation_result = await self.programmer(
                        instruction=f"""Validate this Python function for correctness:
                        - Check syntax errors
                        - Verify it matches the required function signature
                        - Test with basic edge cases (empty input, single element)
                        - Ensure return type matches expected type
                        If errors found, return specific, actionable feedback.
                        If valid, return 'VALID'.""",
                        context=current_candidate,
                        max_retries=1
                    )
                    
                    if "VALID" in validation_result.upper():
                        validated_candidates.append(current_candidate)
                        break
                    else:
                        # Revise based on feedback
                        current_candidate = await self.revise(
                            instruction=f"""Revise the function to fix these issues:
                            {validation_result}
                            Requirements:
                            - Maintain original function signature
                            - Preserve core logic while fixing errors
                            - Handle edge cases explicitly
                            - Output ONLY the corrected function code""",
                            context=current_candidate
                        )
                except Exception as e:
                    # If programmer fails, try one last revision with generic error handling
                    current_candidate = await self.revise(
                        instruction=f"""Make this function more robust:
                        - Add explicit error handling for edge cases
                        - Ensure proper type handling
                        - Verify function signature matches exactly
                        - Output ONLY the corrected function code""",
                        context=current_candidate
                    )
                    break
            
            # Add the final version (even if not fully validated, to have something to ensemble)
            if current_candidate not in validated_candidates:
                validated_candidates.append(current_candidate)

        # Phase 4: Ensemble Selection of Best Solution
        if len(validated_candidates) > 1:
            final_solution = await self.ensemble(
                instruction="""Select the best solution based on:
                1. Correctness (handles edge cases, matches signature)
                2. Readability and maintainability
                3. Efficiency (avoid unnecessary complexity)
                4. Robustness (explicit handling of edge cases)
                5. Adherence to Python best practices
                Return ONLY the selected function code, no explanations or markdown.""",
                contexts_list=validated_candidates
            )
        else:
            final_solution = validated_candidates[0] if validated_candidates else solution_candidates[0]

        # Phase 5: Meta-Validation and Edge Case Simulation
        edge_case_validation = await self.generate(
            instruction=f"""Simulate edge case testing for this solution:
            {final_solution}
            Problem classification: {classification}
            Check for:
            - Empty inputs
            - Single element inputs
            - Boundary values
            - Type consistency
            - Order preservation (if required)
            If any potential issues found, return specific revision instructions.
            If no issues, return 'PASSED'.""",
            context=final_solution
        )

        if "PASSED" not in edge_case_validation.upper():
            # Final revision with explicit edge case handling
            final_solution = await self.revise(
                instruction=f"""Revise to explicitly handle these edge cases:
                {edge_case_validation}
                Requirements:
                - Maintain function signature
                - Add explicit checks for identified edge cases
                - Keep code clean and readable
                - Output ONLY the function code""",
                context=final_solution
            )

        return final_solution