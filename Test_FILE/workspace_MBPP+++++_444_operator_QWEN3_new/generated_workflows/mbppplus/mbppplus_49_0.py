# Workflow ID: mbppplus_49_0
# Benchmark: mbppplus
# Data Indices: [91, 12, 167]

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

        # STEP 1: Deep Structural Analysis - Classify problem type and extract hidden constraints
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Your analysis must include:
            1. Problem Category: Is this primarily mathematical, data structure manipulation, string processing, logical/bitwise, or algorithmic?
            2. Key Operations: What core operations are required? (e.g., modular arithmetic, max extraction, parity counting, filtering)
            3. Input/Output Types: What are the expected input and output data types? Are there type conversion requirements?
            4. Edge Cases: What edge cases must be handled? (empty inputs, single elements, boundary values, duplicates, type mismatches)
            5. Hidden Constraints: Are there unstated constraints or early termination conditions?
            6. Solution Strategy: What general approach would be most appropriate? (iterative, recursive, mathematical formula, built-in functions)
            7. Common Pitfalls: What mistakes are likely based on the problem's phrasing?
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: Parallel Solution Generation - Three different approaches
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using a MATHEMATICAL/FORMULA-BASED approach.
                Problem Classification: {classification}
                
                Requirements:
                - Use mathematical insights or formulas where possible
                - Optimize for correctness over brevity
                - Include handling for all identified edge cases
                - Ensure return type matches expected output
                - Write clean, well-commented code
                - If the problem involves sequences or series, consider closed-form solutions
                - For modular arithmetic, handle large numbers appropriately
                Format as a complete Python function with the exact required signature.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a solution using an ITERATIVE/ALGORITHMIC approach.
                Problem Classification: {classification}
                
                Requirements:
                - Use loops and step-by-step processing
                - Focus on clarity and readability
                - Handle all edge cases explicitly
                - Maintain correct data types throughout
                - Include comments explaining key steps
                - Consider time/space complexity trade-offs
                - For list/tuple operations, preserve order if required
                Format as a complete Python function with the exact required signature.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a solution using a BUILT-IN FUNCTION/OPTIMIZED approach.
                Problem Classification: {classification}
                
                Requirements:
                - Leverage Python's built-in functions and standard library
                - Prioritize efficiency and conciseness
                - Ensure robustness against edge cases
                - Match expected return types precisely
                - Use appropriate data structures (sets for uniqueness, etc.)
                - For mathematical problems, consider math module functions
                - Include brief comments for non-obvious optimizations
                Format as a complete Python function with the exact required signature.""",
                context=classification
            )
        )

        # STEP 3: Parallel Solution Refinement - Critique and improve each attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically revise this solution for maximum robustness and correctness.
                Problem Classification: {classification}
                
                Revision Checklist:
                1. Does it handle ALL edge cases identified in classification?
                2. Are input/output types exactly as required? (list vs tuple vs set)
                3. Is the logic correct for boundary conditions?
                4. Are there any potential off-by-one errors?
                5. Does it handle empty inputs gracefully?
                6. Are variable names clear and consistent?
                7. Is the code efficient without sacrificing correctness?
                8. Are there any type conversion issues?
                9. Does it match the exact function signature required?
                10. Is the solution defensively programmed against unexpected inputs?
                
                Improve the solution based on these criteria. Return ONLY the improved Python function code.""",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # STEP 4: Solution Synthesis - Combine the best elements from all approaches
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the provided candidates.
            Evaluation Criteria:
            1. Correctness: Which solution most accurately solves the problem?
            2. Robustness: Which handles edge cases most comprehensively?
            3. Efficiency: Which has the best time/space complexity?
            4. Readability: Which is clearest and best documented?
            5. Type Safety: Which most precisely matches required input/output types?
            6. Conciseness: Which is most elegant without sacrificing other qualities?
            
            Create a final solution that incorporates the strongest elements from all candidates.
            The output must be ONLY the Python function code with the exact required signature.
            No explanations, no markdown, no additional text - just the function implementation.""",
            contexts_list=refined_solutions
        )

        # STEP 5: Final Validation and Extraction - Ensure clean, executable code
        validated_solution = await self.revise(
            instruction="""Extract and validate the final Python function.
            Requirements:
            1. The output must contain ONLY the function implementation
            2. Must include exact function signature as specified in the problem
            3. Must handle all edge cases identified in classification
            4. Must return correct data types
            5. Must be syntactically valid Python code
            6. Remove any explanatory text, comments, or markdown formatting
            7. Ensure no imports are included unless absolutely necessary (and if so, they must be inside the function)
            
            If the solution doesn't meet these criteria, fix it. Return ONLY the clean Python function code.""",
            context=final_solution
        )

        # STEP 6: Code Extraction - Use regex to ensure we only return the function code
        # This is a safety net to remove any remaining explanatory text
        code_pattern = r'(def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*?\):\s*(?:\n\s+.+)+)'
        match = re.search(code_pattern, validated_solution, re.DOTALL)
        
        if match:
            final_code = match.group(1)
            # Ensure no triple backticks or markdown remain
            final_code = final_code.replace("