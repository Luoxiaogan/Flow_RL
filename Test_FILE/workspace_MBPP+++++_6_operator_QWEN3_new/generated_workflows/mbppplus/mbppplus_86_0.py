# Workflow ID: mbppplus_86_0
# Benchmark: mbppplus
# Data Indices: [371, 221]

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
        import json

        # STEP 1: CLASSIFY PROBLEM TYPE AND COMPLEXITY
        classification = await self.generate(
            instruction="""Perform deep structural classification of this programming problem:
            1. Identify primary operation type: data structure manipulation, string validation, mathematical computation, or logic validation.
            2. Determine complexity level: simple (single operation, no conditionals) vs complex (multiple steps, conditionals, edge cases).
            3. Extract explicit and implicit constraints: input types, output types, boundary conditions, special rules.
            4. Predict likely edge cases: empty inputs, single elements, type boundaries, malformed data.
            5. Suggest appropriate solution strategy: direct implementation, regex, algorithmic decomposition, or multi-step validation.
            Format as JSON with keys: type, complexity, constraints, edge_cases, strategy.""",
            context=""
        )

        # STEP 2: CONDITIONAL BRANCHING BASED ON COMPLEXITY
        if "simple" in classification.lower() and ("tuple" in classification.lower() or "list" in classification.lower() or "concatenate" in classification.lower()):
            # Direct path for simple structural operations
            solution = await self.programmer(
                instruction=f"""Implement the function exactly as specified. Problem context: {classification}
                Requirements:
                - Match function signature precisely
                - Handle edge cases: empty inputs, single elements
                - Return correct data type (tuple vs list)
                - No external libraries unless specified
                - Include minimal defensive checks""",
                context="",
                max_retries=3
            )
        else:
            # Diamond Pattern for complex problems
            # FORK: Generate multiple solution perspectives
            perspectives = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate solution from ALGORITHMIC perspective:
                    Problem: {classification}
                    Focus: Step-by-step procedural logic, loop structures, conditionals.
                    Include edge case handling explicitly.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Generate solution from DECLARATIVE perspective:
                    Problem: {classification}
                    Focus: Pattern matching, regex, set operations, functional approaches.
                    Emphasize conciseness and built-in Python features.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Generate solution from DEFENSIVE PROGRAMMING perspective:
                    Problem: {classification}
                    Focus: Input validation, error handling, boundary checks, type safety.
                    Assume malicious or malformed inputs.""",
                    context=""
                )
            )

            # PROCESS: Refine each perspective
            refined_perspectives = await asyncio.gather(
                *[self.revise(
                    instruction=f"""Improve this solution:
                    - Ensure exact function signature compliance
                    - Add missing edge case handling
                    - Optimize for clarity and efficiency
                    - Verify return type matches specification
                    - Remove any unnecessary complexity""",
                    context=p
                ) for p in perspectives]
            )

            # MERGE: Ensemble best elements
            solution = await self.ensemble(
                instruction="""Synthesize the best solution from all perspectives:
                1. Prioritize correctness and edge case coverage
                2. Choose most readable and maintainable approach
                3. Ensure strict compliance with function signature
                4. Optimize for performance only if not sacrificing clarity
                5. Return only the final implementation code""",
                contexts_list=refined_perspectives
            )

        # STEP 3: STRUCTURAL VALIDATION AND TYPE ENFORCEMENT
        validated_solution = await self.revise(
            instruction=f"""Strictly enforce structural compliance:
            - Function name must match exactly
            - Parameter names and order must be identical
            - Return type must match specification (tuple, list, bool, etc.)
            - No extra imports unless absolutely necessary
            - Must handle all edge cases identified in classification: {classification}
            - Code must be self-contained (no external dependencies)
            Return only the corrected implementation.""",
            context=solution
        )

        # STEP 4: ADVERSARIAL VALIDATION LOOP
        for _ in range(2):  # Two rounds of adversarial testing
            edge_cases = await self.generate(
                instruction=f"""Generate 5 adversarial test cases that might break this solution:
                Solution: {validated_solution}
                Problem constraints: {classification}
                Focus on: type mismatches, boundary values, empty inputs, Unicode, None values, extreme lengths.
                Format as Python assert statements.""",
                context=""
            )
            
            try:
                # Simulate validation (in real system, this would execute tests)
                validation_attempt = await self.programmer(
                    instruction=f"""Test this code against adversarial cases:
                    Code: {validated_solution}
                    Test cases: {edge_cases}
                    If any fail, identify exact failure reason and location.""",
                    context="",
                    max_retries=1
                )
                
                if "fail" in validation_attempt.lower() or "error" in validation_attempt.lower():
                    validated_solution = await self.revise(
                        instruction=f"""Fix the solution based on these failures:
                        Failures: {validation_attempt}
                        Original solution: {validated_solution}
                        Maintain all previous constraints and signature compliance.""",
                        context=validated_solution
                    )
                else:
                    break  # Exit loop if no failures detected
            except Exception:
                # If validation fails catastrophically, proceed with current solution
                break

        # STEP 5: FINAL CLEANUP AND OUTPUT
        final_code = await self.revise(
            instruction="""Final cleanup:
            - Remove any comments or print statements
            - Ensure minimal, clean implementation
            - Verify no external dependencies
            - Return ONLY the function implementation with necessary imports
            - Preserve exact function signature
            - No explanatory text or markdown""",
            context=validated_solution
        )

        return final_code