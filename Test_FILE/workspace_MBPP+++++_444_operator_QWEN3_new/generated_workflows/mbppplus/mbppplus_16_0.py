# Workflow ID: mbppplus_16_0
# Benchmark: mbppplus
# Data Indices: [123, 321, 160]

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

        # Phase 1: Parallel Problem Decomposition
        intent_analysis, constraint_analysis, strategy_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze the core intent of this programming problem:
                - What is the primary mathematical or logical operation being requested?
                - What is the expected input and output?
                - What is the high-level goal (e.g., find maximum, compute sum, validate condition)?
                - Express this in clear, concise terms that capture the essence of what needs to be computed.
                Focus on the 'what' not the 'how'.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all constraints and edge cases:
                - What are the explicit conditions or validations mentioned?
                - What are implicit edge cases (empty inputs, single elements, zeros, negatives, boundaries)?
                - What are the required return types or formats?
                - Are there any special cases that return None, empty, or default values?
                List each constraint clearly and specifically.""",
                context=""
            ),
            self.generate(
                instruction="""Determine the optimal implementation strategy:
                - What algorithmic approach is most suitable (brute force, mathematical formula, iteration, recursion, etc.)?
                - Are there efficiency considerations or known patterns that apply?
                - What data structures or built-in functions might be useful?
                - How should edge cases be handled in code?
                Provide a step-by-step implementation plan.""",
                context=""
            )
        )

        # Phase 2: Synthesize Unified Specification
        problem_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, coherent problem specification:
            1. Combine the intent, constraints, and strategy into a unified document.
            2. Ensure all edge cases from constraint analysis are addressed in the strategy.
            3. Verify that the implementation plan matches the problem intent.
            4. Structure the output as:
               INTENT: [clear statement]
               CONSTRAINTS: [numbered list]
               STRATEGY: [step-by-step plan]
            This specification will guide code generation.""",
            contexts_list=[intent_analysis, constraint_analysis, strategy_analysis]
        )

        # Phase 3: Iterative Code Generation & Validation
        current_code = None
        for iteration in range(3):  # Max 3 revision cycles
            if iteration == 0:
                current_code = await self.generate(
                    instruction=f"""Generate a Python function implementation based EXACTLY on this specification:
                    {problem_spec}
                    
                    CRITICAL REQUIREMENTS:
                    - Use the EXACT function name and parameters from the problem
                    - Include necessary imports INSIDE the function if needed
                    - Handle ALL constraints and edge cases identified
                    - Match return types shown in test cases (tuple vs list vs scalar)
                    - Write clean, efficient, Pythonic code
                    - Return ONLY the function implementation (no explanations, no markdown)
                    
                    Example format:
                    def function_name(param1, param2):
                        # implementation
                        return result""",
                    context=problem_spec
                )
            else:
                # Revise based on validation feedback
                current_code = await self.revise(
                    instruction=f"""Revise the code to fix issues identified in validation:
                    VALIDATION FEEDBACK: {validation_feedback}
                    
                    SPECIFICATION: {problem_spec}
                    
                    REQUIRED FIXES:
                    - Address all validation concerns
                    - Maintain correct function signature
                    - Preserve handling of all edge cases
                    - Ensure return type consistency
                    - Keep code clean and efficient
                    - Return ONLY the raw Python function implementation""",
                    context=current_code
                )

            # Validate the current code
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this code against the specification and domain requirements:
                SPECIFICATION: {problem_spec}
                CODE: {current_code}
                
                CHECKLIST:
                1. Does it handle ALL constraints and edge cases?
                2. Is the return type correct (tuple/list/scalar as required)?
                3. Does the algorithm match the specified strategy?
                4. Are there any syntax errors or logical flaws?
                5. Is it robust against invalid inputs?
                6. Does it follow Python best practices?
                
                If any issues found, describe them SPECIFICALLY. If perfect, say "VALIDATION PASSED".""",
                context=current_code
            )

            if "VALIDATION PASSED" in validation_feedback:
                break

        # Phase 4: Fallback Re-exploration (if validation still failing)
        if "VALIDATION PASSED" not in validation_feedback:
            # Deep re-analysis focusing on missed constraints
            deep_analysis = await self.generate(
                instruction="""Re-analyze the original problem with extreme attention to overlooked details:
                - Re-examine every word for implicit constraints
                - Consider all possible edge cases: empty, single, zero, negative, boundary, type mismatches
                - Look for hidden requirements in test cases
                - What might have been missed in previous analyses?
                Provide a comprehensive constraint and edge case inventory.""",
                context=""
            )
            
            # Merge with original spec and regenerate
            enhanced_spec = await self.ensemble(
                instruction=f"""Enhance the original specification with new insights from deep analysis:
                ORIGINAL SPEC: {problem_spec}
                NEW INSIGHTS: {deep_analysis}
                
                Create an updated specification that incorporates all newly identified constraints and edge cases.
                Structure as before: INTENT, CONSTRAINTS, STRATEGY.""",
                contexts_list=[problem_spec, deep_analysis]
            )
            
            # Final code generation with enhanced spec
            current_code = await self.generate(
                instruction=f"""Generate final implementation using enhanced specification:
                {enhanced_spec}
                
                CRITICAL: Address ALL constraints from both original and enhanced analysis.
                Return ONLY the raw Python function implementation.""",
                context=enhanced_spec
            )

        # Phase 5: Code Extraction (ensure clean output)
        final_code = await self.generate(
            instruction="""Extract ONLY the Python function implementation from the following text.
            Remove any markdown, explanations, or extra text.
            Preserve all imports (place inside function if needed).
            Return ONLY the raw code, nothing else.
            Ensure perfect Python syntax and correct function signature.""",
            context=current_code
        )

        return final_code