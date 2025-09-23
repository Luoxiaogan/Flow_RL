# Workflow ID: mbppplus_18_0
# Benchmark: mbppplus
# Data Indices: [169, 122]

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

        # Step 1: Classify the problem type and requirements
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth. Your analysis must include:
            1. Problem Type: Is this mathematical (involving calculations, sequences, formulas), 
               structural (list/string operations, comparisons, filtering), or algorithmic (searching, sorting, transformations)?
            2. Input/Output Specification: What are the input parameters? What should the return type be? 
               Are there constraints on data types (list vs tuple vs set)?
            3. Edge Cases: What edge cases must be handled? Consider: empty inputs, single elements, 
               duplicates, negative numbers, zero values, maximum/minimum values, type mismatches.
            4. Solution Strategy: What general approach should be used? (e.g., iteration, recursion, 
               built-in functions, mathematical formula, zip/map operations)
            5. Critical Constraints: What must the solution absolutely avoid? (e.g., type errors, 
               inefficient algorithms, missing edge cases)
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Generate comprehensive edge cases based on classification
        edge_cases = await self.generate(
            instruction=f"""Based on the following problem classification:
            {classification}
            
            Generate a comprehensive list of edge case test scenarios. For each edge case:
            - Describe the input scenario (e.g., "empty list", "single element", "all negative numbers")
            - Explain why this edge case is important
            - Provide a concrete example input (if applicable)
            - State what the expected behavior should be
            Focus on robustness: the solution must handle all these cases correctly.
            Format as a numbered list with clear, actionable descriptions.""",
            context=classification
        )

        # Step 3: Generate multiple solution strategies in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Problem Classification:
                {classification}
                
                Edge Cases to Handle:
                {edge_cases}
                
                Generate a complete Python function implementation that solves this problem.
                Strategy 1: Use straightforward iteration and accumulation. Prioritize clarity and correctness.
                - Handle all edge cases identified above
                - Match exact function signature from problem
                - Include necessary imports inside function if needed
                - Return correct data type
                - Add minimal comments only if they clarify non-obvious logic
                Output ONLY the function implementation in a code block.""",
                context=""
            ),
            self.generate(
                instruction=f"""Problem Classification:
                {classification}
                
                Edge Cases to Handle:
                {edge_cases}
                
                Generate a complete Python function implementation that solves this problem.
                Strategy 2: Use functional programming approach (map, filter, reduce, zip, etc.). 
                Prioritize conciseness and Pythonic style.
                - Handle all edge cases identified above
                - Match exact function signature from problem
                - Include necessary imports inside function if needed
                - Return correct data type
                - Add minimal comments only if they clarify non-obvious logic
                Output ONLY the function implementation in a code block.""",
                context=""
            ),
            self.generate(
                instruction=f"""Problem Classification:
                {classification}
                
                Edge Cases to Handle:
                {edge_cases}
                
                Generate a complete Python function implementation that solves this problem.
                Strategy 3: Use mathematical optimization or built-in functions where possible. 
                Prioritize efficiency and elegance.
                - Handle all edge cases identified above
                - Match exact function signature from problem
                - Include necessary imports inside function if needed
                - Return correct data type
                - Add minimal comments only if they clarify non-obvious logic
                Output ONLY the function implementation in a code block.""",
                context=""
            )
        )

        # Step 4: Ensemble - select the best solution
        best_solution = await self.ensemble(
            instruction="""Evaluate the following candidate solutions for the programming problem:
            - Which solution best handles all edge cases?
            - Which solution is most likely to pass all test cases (including hidden ones)?
            - Which solution has the cleanest, most maintainable code?
            - Which solution correctly handles data types and function signatures?
            - Prefer solutions that are simple, correct, and robust over clever but fragile ones.
            Select the single best solution and return it exactly as is (including code block formatting).""",
            contexts_list=solution_attempts
        )

        # Step 5: Validate and revise (up to 2 iterations)
        current_solution = best_solution
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Critically review this solution:
                {current_solution}
                
                Based on the problem classification and edge cases:
                {classification}
                {edge_cases}
                
                Check for:
                1. Correctness: Does it solve the core problem?
                2. Edge Case Handling: Does it handle all identified edge cases?
                3. Type Safety: Does it return the correct data type? Handle input types properly?
                4. Signature Compliance: Does it match the required function signature exactly?
                5. Robustness: Any potential failures or exceptions?
                If any issues are found, provide specific revision instructions. If perfect, say "APPROVED".
                Be extremely thorough—this solution will be submitted as final.""",
                context=current_solution
            )
            
            if "APPROVED" in validation.upper() and "ISSUE" not in validation.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise this solution based on the validation feedback:
                {validation}
                
                Requirements:
                - Fix all identified issues
                - Maintain correct function signature
                - Handle all edge cases
                - Return correct data type
                - Keep code clean and minimal
                Output ONLY the revised function implementation in a code block.""",
                context=current_solution
            )

        # Step 6: Extract clean implementation (ensure no extra text)
        final_implementation = await self.revise(
            instruction="""Extract ONLY the Python function implementation from the text below.
            Requirements:
            - Must include exact function signature from original problem
            - Must include any necessary imports (place inside function if needed)
            - Must be a complete, runnable code block
            - Remove any explanatory text, markdown, or non-code content
            - Preserve all functionality and edge case handling
            Output ONLY the clean code block, nothing else.""",
            context=current_solution
        )

        # Clean up any remaining markdown or extra text
        code_match = re.search(r'