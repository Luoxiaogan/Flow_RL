# Workflow ID: mbppplus_119_0
# Benchmark: mbppplus
# Data Indices: [114, 233]

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
        import json

        # STEP 1: DECOMPOSE THE PROBLEM INTO STRUCTURAL CONSTRAINTS
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its fundamental components. For each, provide detailed analysis:
            1. INPUT SPEC: What is the exact type, structure, and format of input? Include examples.
            2. OUTPUT SPEC: What must the output type and structure be? What are formatting requirements?
            3. TRANSFORMATION RULES: What operations or logic must be applied? Step-by-step if possible.
            4. EDGE CASES: List at least 5 edge cases (empty, single, max/min, malformed, boundary).
            5. VALIDATION CRITERIA: What constitutes a correct solution? What are common failure modes?
            6. SIGNATURE CONSTRAINTS: Any restrictions from the function signature (param names, return type)?
            Format as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # Convert decomposition list to string context
        decomposition_context = "\n".join([
            f"ID: {item['id']}\nDescription: {item['description']}\nDependencies: {item['dependencies']}"
            for item in decomposition
        ])

        # STEP 2: PARALLEL SOLUTION GENERATION - 3 DIFFERENT APPROACHES
        solution_approaches = [
            """Generate a Python function solution using an IMPERATIVE, step-by-step approach:
            - Use explicit loops and conditionals
            - Initialize data structures clearly
            - Handle all edge cases from decomposition
            - Include inline comments explaining key steps
            - Return exact data type specified
            - Do not use external libraries
            - Prioritize readability and correctness over brevity""",
            
            """Generate a Python function solution using a FUNCTIONAL/TRANSFORMATION approach:
            - Use map, filter, comprehensions, recursion where appropriate
            - Focus on data transformation pipelines
            - Handle edge cases through conditional expressions
            - Include type hints in comments if helpful
            - Return exact data type specified
            - Avoid side effects
            - Prioritize elegance and conciseness""",
            
            """Generate a Python function solution using a DECLARATIVE/OPTIMIZED approach:
            - Consider algorithmic efficiency
            - Use built-in functions and standard library optimally
            - Handle edge cases with guard clauses
            - Include performance considerations in comments
            - Return exact data type specified
            - Consider memory usage for large inputs
            - Prioritize robustness and scalability"""
        ]

        # Generate solutions in parallel
        solution_tasks = [
            self.generate(instruction=approach, context=decomposition_context)
            for approach in solution_approaches
        ]
        candidate_solutions = await asyncio.gather(*solution_tasks)

        # STEP 3: ENSEMBLE - SYNTHESIZE BEST HYBRID SOLUTION
        final_solution = await self.ensemble(
            instruction="""Synthesize a final, optimal solution by combining the best elements from all candidates:
            1. PRESERVE FUNCTION SIGNATURE exactly as given in original problem
            2. ENSURE CORRECT RETURN TYPE and structure
            3. INCORPORATE EDGE CASE HANDLING from decomposition
            4. CHOOSE MOST READABLE and MAINTAINABLE logic
            5. IF CONFLICTS EXIST, prioritize correctness and robustness
            6. REWRITE FROM SCRATCH if necessary, using decomposition as spec
            7. INCLUDE COMMENTS for complex logic
            8. VALIDATE against these criteria before finalizing:
               - Handles empty input
               - Handles single element
               - Handles boundary values
               - Matches expected output format exactly
            Return ONLY the function implementation with imports if needed.""",
            contexts_list=candidate_solutions
        )

        # STEP 4: VALIDATE WITH PROGRAMMER (SELF-TESTING)
        for attempt in range(3):  # Max 3 attempts including initial
            validation_result = await self.programmer(
                instruction=f"""Execute this solution against comprehensive test cases. Follow these steps:
                1. Extract function from provided code
                2. Generate test cases covering:
                   - Normal case (from problem examples)
                   - 2 edge cases from decomposition
                   - 1 stress case (large/complex input)
                3. Run tests internally
                4. If all pass: return "SUCCESS"
                5. If any fail: return detailed error message including:
                   - Input that failed
                   - Expected vs Actual output
                   - Likely cause of failure
                   - Specific line or logic to fix
                6. Do NOT modify the code - only report results""",
                context=final_solution,
                max_retries=1
            )

            if "SUCCESS" in validation_result:
                break
            elif attempt < 2:  # Only revise if we have attempts left
                # STEP 5: REVISE BASED ON VALIDATION FEEDBACK
                final_solution = await self.revise(
                    instruction=f"""Fix the solution based on these test failures:
                    {validation_result}
                    
                    Requirements:
                    - PRESERVE original function signature exactly
                    - FIX the specific issues identified
                    - MAINTAIN or IMPROVE edge case handling
                    - DO NOT introduce new bugs
                    - RETURN same data type and structure
                    - Keep code clean and readable
                    - If uncertain, choose conservative/safer approach
                    
                    Return ONLY the corrected function implementation.""",
                    context=final_solution
                )
            else:
                # Final attempt failed - return original synthesized solution
                break

        return final_solution