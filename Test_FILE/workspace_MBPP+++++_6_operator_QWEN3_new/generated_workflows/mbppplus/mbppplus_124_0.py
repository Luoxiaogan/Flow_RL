# Workflow ID: mbppplus_124_0
# Benchmark: mbppplus
# Data Indices: [326, 34]

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

        # Step 1: Decompose the problem into core dimensions
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into exactly four subproblems:
            1. INPUT_SPEC: Describe the input parameters - their types, structure, and any constraints.
            2. OUTPUT_SPEC: Describe the expected return value - type, structure, and format requirements.
            3. ALGORITHM_PATTERN: Identify the algorithmic approach or computational pattern needed (e.g., recursion, sorting, traversal).
            4. EDGE_CASES: List at least three edge cases or boundary conditions that must be handled.
            Return each as a separate subproblem with clear ID and description.""",
            context=""
        )
        
        # Convert decomposition to readable context
        decomposition_context = "\n".join([
            f"{item['id']}: {item['description']}" 
            for item in decomposition
        ])

        # Step 2: Parallel analysis from three perspectives
        analysis_tasks = [
            self.generate(
                instruction=f"""Analyze from ALGORITHMIC perspective:
                Given problem decomposition:
                {decomposition_context}
                
                Focus on:
                - What established algorithms or patterns fit this problem?
                - What are the time/space complexity considerations?
                - Are there multiple valid approaches? Which is most appropriate?
                - What are common pitfalls for this algorithm type?
                Provide detailed reasoning.""",
                context=decomposition_context
            ),
            self.generate(
                instruction=f"""Analyze from EDGE CASE perspective:
                Given problem decomposition:
                {decomposition_context}
                
                Focus on:
                - What are ALL possible edge cases beyond those listed?
                - How should each edge case be handled in code?
                - What input values might cause failures (empty, null, extreme values)?
                - What are the boundary conditions for loops/recursion?
                List each edge case with handling strategy.""",
                context=decomposition_context
            ),
            self.generate(
                instruction=f"""Analyze from INTERFACE SPECIFICATION perspective:
                Given problem decomposition:
                {decomposition_context}
                
                Focus on:
                - Exact function signature including parameter names and types
                - Exact return type and structure (list vs tuple vs set, order preservation)
                - Any implicit constraints from test cases or problem context
                - Required imports or external dependencies
                Provide a precise, unambiguous specification.""",
                context=decomposition_context
            )
        ]
        
        analysis_results = await asyncio.gather(*analysis_tasks)

        # Step 3: Ensemble analyses into unified specification
        unified_spec = await self.ensemble(
            instruction="""Synthesize these three analyses into a single, unambiguous implementation specification:
            - Resolve any contradictions by choosing the most conservative/safest approach
            - Explicitly state the function signature with parameter types and return type
            - List ALL edge cases that must be handled, with brief handling notes
            - Specify any required imports
            - Note any performance or complexity requirements
            Format as a structured specification document.""",
            contexts_list=analysis_results
        )

        # Step 4: Generate and refine code with iterative validation
        final_code = None
        for attempt in range(3):  # Up to 3 attempts
            # Generate code based on unified spec
            code_attempt = await self.programmer(
                instruction=f"""Implement the function EXACTLY as specified below. 
                Specification:
                {unified_spec}
                
                Requirements:
                - Match function signature exactly
                - Handle all specified edge cases explicitly
                - Use clear, readable code over clever optimizations
                - Include type hints if types are inferable
                - Add minimal comments only for non-obvious logic
                - Return correct data type (list/tuple/set) as specified
                - Do NOT include test cases or example usage""",
                context=unified_spec,
                max_retries=1
            )
            
            # Validate and revise code
            revised_code = await self.revise(
                instruction=f"""Critically review this code against the original problem and specification:
                Original Problem: {self.problem_text}
                Specification: {unified_spec}
                
                Check for:
                1. Function signature compliance (name, parameters, return type)
                2. Handling of all specified edge cases
                3. Potential bugs (off-by-one, recursion base cases, type mismatches)
                4. Readability and maintainability
                5. Adherence to specification details
                
                If ANY issues are found, revise the code to fix them.
                If no issues, return the code unchanged.
                Preserve exact function signature and return type.""",
                context=code_attempt
            )
            
            # Check if revision found fundamental issues requiring regeneration
            if "fundamental flaw" in revised_code.lower() or "incorrect approach" in revised_code.lower():
                continue  # Try again with same spec
            else:
                final_code = revised_code
                break
        
        if final_code is None:
            final_code = code_attempt  # Fallback to last attempt

        # Final sanity check summary
        sanity_check = await self.summarize(
            instruction=f"""Summarize in 3 sentences:
            1. How the final code complies with the specification
            2. What edge cases are explicitly handled
            3. Any potential remaining risks or limitations
            If any part of the specification is unaddressed, explicitly flag it.""",
            context=f"Specification: {unified_spec}\n\nCode: {final_code}"
        )

        # Return the final code (extract just the code portion if programmer output includes extra text)
        # Look for code block or function definition
        code_lines = []
        in_code = False
        for line in final_code.split('\n'):
            if line.strip().startswith('def ') or line.strip().startswith('import '):
                in_code = True
            if in_code:
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines)
        else:
            return final_code  # Fallback