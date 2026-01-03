# Workflow ID: mbppplus_84_0
# Benchmark: mbppplus
# Data Indices: [168, 98, 342]

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
        Universal workflow for programming problem-solving domain.
        Dynamically adapts strategy based on problem characteristics.
        Handles edge cases, type consistency, and validation intrinsically.
        """
        import asyncio
        import re

        # PHASE 1: PARALLEL ANALYSIS & CLASSIFICATION
        analysis_tasks = await asyncio.gather(
            self.generate(
                instruction="""Perform deep problem analysis. Identify:
                1. Problem category (set ops, string manipulation, math, etc.)
                2. Input/output data types and constraints
                3. Edge cases (empty inputs, single elements, duplicates, boundaries)
                4. Order preservation requirements
                5. Error conditions or special return values
                6. Algorithmic approach (set operations, iteration, sorting, etc.)
                Format as structured JSON-like text with clear section headers.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all implicit requirements not stated in function signature:
                - What should happen with empty inputs?
                - Are duplicates allowed? Should they be preserved?
                - Is order important? If so, whose order?
                - Are there type conversion requirements?
                - Any special return values (like 'Not Possible')?
                - Performance constraints (if any)?
                Present as bullet-point list with justification from problem context.""",
                context=""
            )
        )
        
        problem_analysis, implicit_requirements = analysis_tasks

        # PHASE 2: GENERATE MULTIPLE SOLUTION CANDIDATES IN PARALLEL
        candidate_tasks = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python solution with focus on correctness and edge cases.
                Problem Analysis: {problem_analysis}
                Implicit Requirements: {implicit_requirements}
                
                Guidelines:
                - Handle all edge cases explicitly
                - Preserve required data types (list vs tuple vs set)
                - Maintain order if specified
                - Return appropriate special values for error conditions
                - Include defensive checks for input validity
                - Code must be self-contained (include necessary imports)
                - Match exact function signature from problem
                - Prioritize clarity over premature optimization
                
                Return ONLY the function implementation as specified in output requirements.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate alternative Python solution with focus on efficiency and elegance.
                Problem Analysis: {problem_analysis}
                Implicit Requirements: {implicit_requirements}
                
                Guidelines:
                - Use most appropriate data structures for the task
                - Consider time/space complexity
                - Leverage Python built-ins and standard library
                - Still handle all edge cases
                - Maintain readability
                - Same function signature and return type requirements
                
                Return ONLY the function implementation as specified in output requirements.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate defensive Python solution with extensive error handling.
                Problem Analysis: {problem_analysis}
                Implicit Requirements: {implicit_requirements}
                
                Guidelines:
                - Validate input types and structures
                - Handle unexpected inputs gracefully
                - Include comments explaining edge case handling
                - Use explicit conditionals rather than clever one-liners
                - Same function signature and return type requirements
                
                Return ONLY the function implementation as specified in output requirements.""",
                context=""
            )
        )
        
        candidate1, candidate2, candidate3 = candidate_tasks

        # PHASE 3: VALIDATION & REFINEMENT
        validation = await self.generate(
            instruction=f"""Critically evaluate all three candidate solutions:
            Candidate 1: {candidate1}
            Candidate 2: {candidate2} 
            Candidate 3: {candidate3}
            
            Check for:
            - Correct handling of edge cases identified in analysis
            - Type consistency (input/output types match requirements)
            - Order preservation where required
            - Special return values for error conditions
            - Code robustness (no assumptions about input validity)
            - Adherence to function signature
            - Potential bugs or logical errors
            
            Return detailed critique with specific line numbers or code snippets that need fixing.
            If all candidates are acceptable, state "ALL_VALID".""",
            context=f"{problem_analysis}\n\n{implicit_requirements}"
        )

        # Conditional refinement based on validation
        if "ALL_VALID" not in validation:
            # Revise the first candidate based on validation feedback
            refined_candidate = await self.revise(
                instruction=f"""Improve the solution based on this validation feedback:
                {validation}
                
                Specific requirements:
                - Fix all identified issues
                - Maintain function signature exactly
                - Preserve all edge case handling
                - Keep code clean and readable
                - Include necessary imports at top
                - Return appropriate data types
                
                Return ONLY the corrected function implementation.""",
                context=candidate1
            )
            final_candidates = [refined_candidate, candidate2, candidate3]
        else:
            final_candidates = [candidate1, candidate2, candidate3]

        # PHASE 4: ENSEMBLE SYNTHESIS
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these candidates:
            {final_candidates}
            
            Selection criteria:
            1. Correctness (must handle all edge cases)
            2. Robustness (defensive programming, input validation)
            3. Readability and maintainability
            4. Efficiency (appropriate for problem scale)
            5. Adherence to exact function signature and return types
            6. Clean code practices
            
            If candidates have complementary strengths, merge them.
            Prioritize correctness and edge case handling above all else.
            Return ONLY the final function implementation as specified in output requirements.""",
            contexts_list=final_candidates
        )

        # PHASE 5: FINAL SANITY CHECK (Optional revision if obvious issues remain)
        sanity_check = await self.generate(
            instruction=f"""Perform final sanity check on this solution:
            {final_solution}
            
            Verify:
            - Function name matches exactly
            - All imports included
            - No extra text or explanations
            - Returns correct data type
            - Handles empty inputs
            - Matches expected behavior from problem examples
            
            If any issues found, describe them concisely. Otherwise, respond "OK".""",
            context=""
        )

        if "OK" not in sanity_check:
            final_solution = await self.revise(
                instruction=f"""Fix these final issues:
                {sanity_check}
                
                Return ONLY the corrected function implementation with exact required format.""",
                context=final_solution
            )

        return final_solution