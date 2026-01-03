# Workflow ID: humaneval_68_0
# Benchmark: humaneval
# Data Indices: [56, 76]

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

        # Step 1: Classify the problem to determine workflow depth
        classification = await self.generate(
            instruction="""Analyze this code generation problem and classify it along these dimensions:
            1. Primary domain: Is it string manipulation, mathematical, list/array processing, or algorithmic/state-based?
            2. Complexity level: Simple (direct pattern), Medium (requires iteration or conditionals), Complex (multiple edge cases or non-obvious invariant)
            3. Key constraints from examples: What do the examples reveal about edge cases, base conditions, or hidden rules?
            4. Return type: What exact type must be returned (bool, int, float, string, etc.)?
            5. Critical patterns: What recurring operations or structures appear in the examples?
            Provide a structured classification that will guide solution strategy selection.""",
            context=""
        )

        # Step 2: Extract function name for final sanitization
        function_name = await self.generate(
            instruction="""Extract the exact function name from the ENTRY POINT section of the problem. 
            Return ONLY the function name as a string, nothing else. This will be used to enforce naming in the final output.""",
            context=""
        )
        function_name = function_name.strip().strip('"').strip("'")

        # Step 3: Conditional branching based on complexity
        if "simple" in classification.lower() and "medium" not in classification.lower() and "complex" not in classification.lower():
            # Lightweight path for simple problems
            solution = await self.generate(
                instruction=f"""Generate a Python function implementation based on the specification and examples.
                Classification context: {classification}
                - Function name must be: {function_name}
                - Return type must match examples exactly
                - Handle all edge cases shown in examples
                - Code must be minimal and precise
                - Do not include any explanations or comments
                - Return only the function definition""",
                context=""
            )
            
            # Single revision for validation
            refined = await self.revise(
                instruction=f"""Critically review this code against the problem specification and examples:
                - Does it handle ALL provided examples correctly?
                - Are there any edge cases it might miss?
                - Is the return type exactly as required?
                - Is the function name exactly '{function_name}'?
                - Fix any issues found. Return only the corrected function code, nothing else.""",
                context=solution
            )
            final_solution = refined

        else:
            # Heavyweight path for medium/complex problems
            # Generate 3 diverse solution candidates in parallel
            candidate_instructions = [
                f"""Generate a solution using a SIMULATION/PROCEDURAL approach:
                Classification context: {classification}
                - Simulate the process step by step as shown in examples
                - Use counters, flags, or state variables if needed
                - Handle edge cases explicitly
                - Function name: {function_name}
                - Return only the function code""",
                
                f"""Generate a solution using a MATHEMATICAL/FORMULA-BASED approach:
                Classification context: {classification}
                - Derive a mathematical formula or pattern from the examples
                - Use arithmetic, logarithms, or algebraic manipulation if applicable
                - Function name: {function_name}
                - Return only the function code""",
                
                f"""Generate a solution focusing on EDGE CASES and INVARIANTS:
                Classification context: {classification}
                - Identify invariants that must always hold true
                - Design solution around preserving these invariants
                - Explicitly handle all edge cases from examples
                - Function name: {function_name}
                - Return only the function code"""
            ]
            
            candidates = await asyncio.gather(
                *[self.generate(instruction=instr, context="") for instr in candidate_instructions]
            )
            
            # Summarize each candidate for ensemble (compress to key logic)
            summaries = await asyncio.gather(
                *[self.summarize(
                    instruction="Extract the core algorithm and key edge case handling. Ignore boilerplate. Focus on the essential logic.",
                    context=cand
                ) for cand in candidates]
            )
            
            # Ensemble: Select or synthesize best solution
            final_solution = await self.ensemble(
                instruction=f"""Select the best solution based on:
                1. Correctness: Must handle all examples and edge cases
                2. Simplicity: Prefer clear, minimal code
                3. Robustness: Must not fail on edge cases
                4. Match: Function name must be '{function_name}' and return type exact
                If one solution is clearly superior, select it. Otherwise, synthesize a hybrid that combines the best elements.
                Return ONLY the final function code, nothing else.""",
                contexts_list=candidates  # Use full candidates, not summaries, for final output
            )
            
            # Validation and refinement loop (up to 2 iterations)
            for _ in range(2):
                validation = await self.generate(
                    instruction=f"""Perform strict validation:
                    - Does this code pass ALL examples in the docstring?
                    - Are there any logical flaws or edge cases missed?
                    - Is the return type exact?
                    - Is the function name exactly '{function_name}'?
                    If perfect, respond with 'VALID'. Otherwise, describe exactly what's wrong.""",
                    context=final_solution
                )
                
                if "valid" in validation.lower() and "not" not in validation.lower() and "invalid" not in validation.lower():
                    break  # Exit if validated
                    
                # Revise based on validation feedback
                final_solution = await self.revise(
                    instruction=f"""Fix the issues identified in validation:
                    Validation feedback: {validation}
                    - Preserve correct parts
                    - Fix only what's broken
                    - Maintain function name '{function_name}'
                    - Return only the corrected function code""",
                    context=final_solution
                )

        # Final sanitization: Ensure exact function name and clean format
        sanitized = await self.revise(
            instruction=f"""Final sanitization:
            1. Ensure function definition starts exactly with 'def {function_name}'
            2. Remove any extra text, comments, or explanations
            3. Ensure code is properly indented and syntactically correct
            4. Return ONLY the function code, nothing before or after""",
            context=final_solution
        )
        
        return sanitized