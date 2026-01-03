# Workflow ID: mbppplus_58_0
# Benchmark: mbppplus
# Data Indices: [256, 229, 357]

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

        # STEP 1: Deep Problem Classification
        classification = await self.generate(
            instruction="""Perform comprehensive problem classification. Analyze the task and produce a structured breakdown with these exact fields:
            - problem_category: One of [list_transformation, mathematical_rounding, symbolic_encoding, set_operations, logic_validation, other]
            - input_types: List of expected input types (e.g., ['list', 'int', 'float'])
            - output_type: Expected return type (e.g., 'list', 'tuple', 'str', 'int')
            - edge_cases: List of edge cases to handle (e.g., ['empty_input', 'single_element', 'whitespace', 'negative_numbers'])
            - algorithmic_approach: Suggested strategy (e.g., 'map_conversion', 'ceil_with_precision', 'greedy_symbol_substitution')
            - critical_constraints: Any must-follow rules from domain overview (e.g., 'preserve_whitespace', 'no_external_libraries', 'return_exact_type')
            
            Base your analysis strictly on the problem description and domain requirements. Be exhaustive and precise.""",
            context=""
        )

        # STEP 2: Parallel Solution Generation (3 strategic perspectives)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a DIRECT implementation solution focusing on LITERAL REQUIREMENTS.
                Classification context: {classification}
                
                Rules:
                - Implement exactly what the problem asks, no more no less
                - Use simplest possible approach that satisfies basic test cases
                - Do NOT optimize prematurely
                - Include necessary imports inside function if needed
                - Return EXACT data type specified in classification""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a ROBUST implementation solution focusing on EDGE CASES and DEFENSIVE PROGRAMMING.
                Classification context: {classification}
                
                Rules:
                - Handle ALL edge cases listed in classification
                - Add input validation if domain allows
                - Use explicit type handling (e.g., str(), list(), int())
                - Include guard clauses for empty/single inputs
                - Return EXACT data type specified in classification""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an IDIOMATIC implementation solution focusing on PYTHONIC EFFICIENCY and BUILT-INS.
                Classification context: {classification}
                
                Rules:
                - Use most appropriate Python built-ins and idioms (map, list comprehensions, math module, etc.)
                - Prioritize readability and conciseness
                - Avoid unnecessary loops - use functional approaches where possible
                - Include necessary imports inside function
                - Return EXACT data type specified in classification""",
                context=""
            )
        )

        # STEP 3: Parallel Solution Validation
        validated_solutions = []
        for i, solution in enumerate(solution_attempts):
            validation = await self.revise(
                instruction=f"""CRITICALLY VALIDATE this solution against classification and domain rules.
                Classification: {classification}
                
                Validation checklist:
                1. Does it handle ALL specified edge cases?
                2. Does it return EXACTLY the required data type?
                3. Are all necessary imports included inside function?
                4. Does it avoid forbidden patterns (e.g., external libraries without import)?
                5. Is it consistent with domain best practices?
                
                If any issues found, annotate them clearly. If perfect, state 'VALIDATED'.
                Do NOT rewrite - only critique and annotate.""",
                context=solution
            )
            # Combine solution with its validation for ensemble
            validated_solutions.append(f"SOLUTION:\n{solution}\n\nVALIDATION:\n{validation}")

        # STEP 4: Synthesize Best Solution
        synthesized = await self.ensemble(
            instruction=f"""SYNTHESIZE the optimal solution by combining the best elements from all validated attempts.
            Classification: {classification}
            
            Synthesis rules:
            1. Take core algorithm from most correct implementation
            2. Borrow edge-case handling from most robust solution
            3. Adopt idiomatic patterns from most Pythonic solution
            4. Ensure EXACT return type compliance
            5. Include ONLY necessary imports inside function
            6. Preserve all validation fixes
            
            Output ONLY the final function implementation - no explanations, no markdown.
            Format exactly as required: imports first, then function definition.""",
            contexts_list=validated_solutions
        )

        # STEP 5: Self-Consistency Check (Meta-validation)
        consistency_check = await self.generate(
            instruction=f"""Perform META-VALIDATION on this solution:
            {synthesized}
            
            Check for:
            - Any remaining edge cases not handled?
            - Type mismatches between return statement and required type?
            - Missing imports for used functions/modules?
            - Assumptions about input validity not stated in problem?
            - Violations of domain best practices?
            
            If ANY issues found, describe them specifically. If perfect, output 'CONSISTENT'.""",
            context=synthesized
        )

        # STEP 6: Conditional Refinement Loop (max 1 iteration)
        final_solution = synthesized
        if "CONSISTENT" not in consistency_check.upper():
            # Attempt refinement based on consistency feedback
            refined = await self.revise(
                instruction=f"""REFINE this solution to fix ALL issues identified in consistency check.
                Consistency feedback: {consistency_check}
                Classification: {classification}
                
                Rules:
                - Address EVERY specific issue mentioned
                - Maintain all previously validated correct behavior
                - Do NOT introduce new functionality
                - Preserve exact function signature and return type
                - Output ONLY the corrected implementation""",
                context=synthesized
            )
            final_solution = refined

        # STEP 7: Nuclear Option Fallback (if still inconsistent)
        consistency_recheck = await self.generate(
            instruction=f"""FINAL VALIDATION: Is this solution now fully consistent?
            {final_solution}
            
            Answer ONLY 'YES' or 'NO'.""",
            context=final_solution
        )

        if "YES" not in consistency_recheck.upper():
            # Nuclear reset - ignore all prior attempts
            final_solution = await self.generate(
                instruction=f"""NUCLEAR RESET: Generate MINIMAL CORRECT SOLUTION ignoring all prior attempts.
                Problem: {self.problem_text}
                Classification: {classification}
                
                Rules:
                - Focus ONLY on passing test cases shown in problem
                - Use simplest possible implementation
                - Handle only explicitly required edge cases
                - Include necessary imports
                - Return EXACT required type
                - Output ONLY function implementation""",
                context=""
            )

        return final_solution