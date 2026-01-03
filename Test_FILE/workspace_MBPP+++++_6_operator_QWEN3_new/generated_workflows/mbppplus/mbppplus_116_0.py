# Workflow ID: mbppplus_116_0
# Benchmark: mbppplus
# Data Indices: [181, 309]

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

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break this programming problem into atomic subproblems. For each, specify:
            1. The core computational/mathematical task
            2. Required input/output types and structures
            3. All edge cases (empty, single element, boundaries, type variations)
            4. Any implicit constraints (order preservation, mutability, performance)
            5. Known algorithms or patterns that might apply
            Return as structured subproblems with dependencies if any.""",
            context=""
        )

        # Step 2: Parallel analysis - algorithmic, structural, and edge-case perspectives
        algorithmic_analysis, type_analysis, edge_case_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze the algorithmic essence of this problem:
                - What computational patterns apply? (e.g., sliding window, prefix sum, recursion, greedy)
                - Are there mathematical optimizations or formulas?
                - What is the expected time/space complexity?
                - Reference similar known problems or algorithms.
                Be specific and technical.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze data types and structural requirements:
                - What are the exact input and output types? (list, tuple, set, string, int, etc.)
                - Are there constraints on mutability, order, or duplication?
                - Should the solution preserve input order or can it be rearranged?
                - Are there type conversion requirements? (e.g., string to int)
                - What Python data structures are most appropriate?""",
                context=""
            ),
            self.generate(
                instruction="""Enumerate ALL edge cases and boundary conditions:
                - Empty inputs, single-element inputs, maximum/minimum values
                - Type edge cases (None, mixed types, unexpected formats)
                - Domain-specific boundaries (e.g., leap years for dates, negative indices for arrays)
                - Performance boundaries (very large inputs, recursion limits)
                - Invalid inputs that should be handled gracefully.
                List exhaustively with examples.""",
                context=""
            )
        )

        # Step 3: Synthesize analyses into a unified specification
        synthesis = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, coherent problem specification:
            1. Core algorithmic approach (from algorithmic analysis)
            2. Data type and structure requirements (from type analysis)
            3. Complete edge case coverage (from edge case analysis)
            4. Validation criteria and constraints
            Resolve any contradictions by prioritizing edge-case robustness and type safety.
            Format as a structured specification that can guide code generation.""",
            contexts_list=[algorithmic_analysis, type_analysis, edge_case_analysis]
        )

        # Step 4: Generate initial code implementation
        initial_code = await self.programmer(
            instruction=f"""Implement a solution based on this specification:
            {synthesis}
            
            Requirements:
            - Use the exact function signature from the problem
            - Include all necessary imports
            - Handle all enumerated edge cases
            - Return correct data types
            - Write clean, efficient, readable code
            - No extra text or explanations — only the function implementation""",
            context=synthesis
        )

        # Step 5: Revise for edge cases and type safety
        revised_code = await self.revise(
            instruction=f"""Critically review this code:
            {initial_code}
            
            Check for:
            1. All edge cases listed in specification: {edge_case_analysis}
            2. Correct input/output types and conversions
            3. Efficiency — avoid unnecessary loops or operations
            4. Readability and proper variable naming
            5. Adherence to exact function signature
            If any issues, provide precise fixes. Return only the corrected implementation.""",
            context=initial_code
        )

        # Step 6: Adaptive validation loop (max 2 retries)
        current_code = revised_code
        for attempt in range(2):
            validation_result = await self.programmer(
                instruction="""Execute this code against basic test cases from the problem.
                If all tests pass, return 'VALID'.
                If any test fails, return the exact error message and failing input.
                Do not modify the code — only report pass/fail with errors.""",
                context=current_code
            )
            
            if "VALID" in validation_result:
                break
            else:
                # Debug and fix based on error
                current_code = await self.revise(
                    instruction=f"""The code failed with error: {validation_result}
                    Fix this specific failure while preserving all other functionality.
                    Ensure edge cases and type requirements are still met.
                    Return only the corrected implementation.""",
                    context=current_code
                )
        else:
            # Fallback: Reframe and regenerate if still failing
            reframed_approaches = await asyncio.gather(
                self.generate(
                    instruction="""Reframe this problem as a dynamic programming or state machine problem.
                    What would a DP solution look like? Define states and transitions.""",
                    context=""
                ),
                self.generate(
                    instruction="""Reframe this problem using alternative algorithms:
                    - Brute force with pruning
                    - Greedy approach
                    - Mathematical formula
                    - Recursive decomposition
                    Propose at least two alternative solution strategies.""",
                    context=""
                )
            )
            
            # Ensemble with original approach
            final_approach = await self.ensemble(
                instruction="""Select the most robust solution approach from:
                1. Original approach
                2. Dynamic programming/state machine reframing
                3. Alternative algorithmic reframing
                Prioritize approaches that handle edge cases and match problem constraints.
                Return the selected approach as a clear implementation specification.""",
                contexts_list=[synthesis] + reframed_approaches
            )
            
            # Final code generation
            current_code = await self.programmer(
                instruction=f"""Implement based on selected approach:
                {final_approach}
                
                Requirements:
                - Exact function signature
                - Handle all edge cases
                - Correct data types
                - Clean, efficient code
                - Only return the function implementation""",
                context=final_approach
            )

        # Step 7: Final cleanup and extraction
        final_implementation = await self.summarize(
            instruction="""Extract ONLY the final function implementation from this text.
            Remove any markdown, explanations, or extra text.
            Ensure imports are included and function signature matches exactly.
            Return pure Python code ready for execution.""",
            context=current_code
        )

        return final_implementation