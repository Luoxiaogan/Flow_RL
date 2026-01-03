# Workflow ID: mbppplus_114_0
# Benchmark: mbppplus
# Data Indices: [282, 30, 41]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for programming problem solving domain.
        Handles list operations, string manipulations, mathematical computations,
        and data structure algorithms with edge case awareness.
        """
        import asyncio
        import re

        # Phase 1: Deep problem analysis and decomposition
        problem_analysis = await self.generate(
            instruction="""Perform comprehensive structural analysis of this programming problem:
            1. Identify the exact transformation required (filter, map, reduce, etc.)
            2. Determine input and output data types (list, tuple, set, string, etc.)
            3. Extract key constraints and edge cases (empty inputs, single elements, boundaries)
            4. Analyze test cases to infer behavior patterns and type requirements
            5. Identify any mathematical or logical operations needed
            6. Note any order preservation requirements
            7. Determine if duplicates should be handled specially
            8. Extract function signature and parameter meanings
            Present analysis as structured JSON-like format with clear sections.""",
            context=""
        )

        # Phase 2: Parallel solution strategy exploration
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a direct, literal implementation based on problem requirements:
                Problem Analysis: {problem_analysis}
                
                Requirements:
                - Implement exactly what's asked, no optimizations
                - Handle all edge cases identified in analysis
                - Preserve exact data types (list vs tuple vs set)
                - Include clear variable names and straightforward logic
                - Return correct type as specified in function signature
                - Include necessary imports at top of function
                Output ONLY the function implementation in required format.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate an optimized, algorithmically efficient implementation:
                Problem Analysis: {problem_analysis}
                
                Requirements:
                - Use most efficient approach (filter, comprehensions, built-ins)
                - Consider mathematical optimizations where applicable
                - Handle edge cases explicitly
                - Preserve required data types and order
                - Include necessary imports
                - Focus on performance while maintaining correctness
                Output ONLY the function implementation in required format.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a defensively programmed, edge-case hardened implementation:
                Problem Analysis: {problem_analysis}
                
                Requirements:
                - Explicitly handle all edge cases (empty, single element, boundaries)
                - Include input validation if appropriate
                - Use clear, defensive programming patterns
                - Preserve exact return types
                - Include comprehensive error handling for unexpected inputs
                - Include necessary imports
                Output ONLY the function implementation in required format.""",
                context=problem_analysis
            )
        ]
        
        # Execute strategies in parallel
        strategy_results = await asyncio.gather(*strategy_tasks)

        # Phase 3: Synthesize best solution from parallel strategies
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all candidate solutions into one optimal implementation:
            Evaluation Criteria (in order of priority):
            1. CORRECTNESS: Must handle all edge cases and match expected behavior
            2. TYPE CONSISTENCY: Must use correct data types (list, tuple, set) as required
            3. SIMPLICITY: Prefer straightforward, readable code over clever optimizations
            4. EFFICIENCY: Use efficient algorithms when it doesn't compromise clarity
            5. DEFENSIVE PROGRAMMING: Include edge case handling but avoid unnecessary complexity
            
            Synthesis Rules:
            - Take the most complete edge case handling from any solution
            - Prefer simplest correct implementation for core logic
            - Ensure return type matches exactly what's required
            - Include only necessary imports
            - Remove any redundant or defensive code that doesn't add value
            - Preserve function signature exactly as specified
            
            Output ONLY the final function implementation in required format.""",
            contexts_list=strategy_results
        )

        # Phase 4: Validation and refinement loop
        final_solution = synthesized_solution
        for iteration in range(3):  # Maximum 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate this implementation against problem requirements:
                Implementation: {final_solution}
                Problem Analysis: {problem_analysis}
                
                Check for:
                1. Correct handling of all edge cases identified in analysis
                2. Exact match of input/output types (list, tuple, set, etc.)
                3. Correct behavior for sample test cases (if provided)
                4. Proper imports included
                5. Function signature matches exactly
                6. No unnecessary complexity or defensive code
                7. Efficient and readable implementation
                
                If any issues found, describe them specifically. If perfect, say "VALIDATED".
                Be extremely thorough - this is the final quality check.""",
                context=final_solution
            )
            
            if "VALIDATED" in validation.upper() and "ISSUE" not in validation.upper() and "ERROR" not in validation.upper():
                break
            else:
                final_solution = await self.revise(
                    instruction=f"""Fix all issues identified in validation:
                    Current Implementation: {final_solution}
                    Validation Feedback: {validation}
                    Problem Analysis: {problem_analysis}
                    
                    Requirements:
                    - Fix all identified issues while preserving correct functionality
                    - Maintain exact function signature
                    - Preserve correct data types
                    - Keep code as simple and readable as possible
                    - Include necessary imports
                    - Ensure all edge cases are handled
                    Output ONLY the revised function implementation in required format.""",
                    context=final_solution
                )

        return final_solution