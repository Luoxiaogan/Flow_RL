# Workflow ID: mbppplus_37_0
# Benchmark: mbppplus
# Data Indices: [297, 256]

import asyncio

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

        # Step 1: Deep problem analysis - extract intent, edge cases, constraints
        problem_analysis = await self.generate(
            instruction="""Perform a deep semantic analysis of this programming problem. Your analysis must include:
            1. Core objective: What is the function supposed to accomplish? (Not just what it does, but why)
            2. Input/Output contract: What are the exact types and structures expected for input and output?
            3. Edge cases: List at least 5 potential edge cases (empty inputs, single elements, duplicates, boundaries, etc.)
            4. Common misinterpretations: What are typical mistakes or misunderstandings programmers might have?
            5. Algorithmic category: Is this a filtering, transformation, aggregation, search, or other type of problem?
            6. Pythonic approaches: What built-in functions, itertools, or standard library tools are most suitable?
            7. Type handling: Must order be preserved? Are duplicates allowed? Should return type be list/tuple/set?
            Present your analysis in clear, structured sections with bullet points where appropriate.""",
            context=""
        )

        # Step 2: Generate multiple solution approaches in parallel
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python solution using FUNCTIONAL PROGRAMMING principles (map, filter, reduce, comprehensions).
                Problem Analysis Context:
                {problem_analysis}
                
                Requirements:
                - Use list comprehensions or built-in functions where possible
                - Handle all edge cases mentioned in the analysis
                - Return correct data type as specified
                - Include necessary imports inside the function if needed
                - Function signature must exactly match the required signature
                - Return ONLY the function implementation, no explanations or markdown""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a Python solution using IMPERATIVE/PROCEDURAL programming (loops, counters, conditionals).
                Problem Analysis Context:
                {problem_analysis}
                
                Requirements:
                - Use for/while loops and explicit conditionals
                - Handle all edge cases mentioned in the analysis
                - Return correct data type as specified
                - Include necessary imports inside the function if needed
                - Function signature must exactly match the required signature
                - Return ONLY the function implementation, no explanations or markdown""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a Python solution using PYTHON STANDARD LIBRARY utilities (itertools, collections, etc.).
                Problem Analysis Context:
                {problem_analysis}
                
                Requirements:
                - Leverage itertools, collections, or other standard library modules
                - Handle all edge cases mentioned in the analysis
                - Return correct data type as specified
                - Include necessary imports inside the function if needed
                - Function signature must exactly match the required signature
                - Return ONLY the function implementation, no explanations or markdown""",
                context=problem_analysis
            )
        )

        # Step 3: Ensemble - synthesize best solution from candidates
        synthesized_solution = await self.ensemble(
            instruction="""You are an expert Python code reviewer. Your task is to select or synthesize the best solution from the candidates below.
            Evaluation criteria:
            1. Correctness: Does it handle all edge cases? Is the logic sound?
            2. Robustness: Does it gracefully handle unexpected inputs?
            3. Readability: Is the code clear and Pythonic?
            4. Efficiency: Is it reasonably efficient for the problem size?
            5. Type compliance: Does it return exactly the required type?
            6. Signature compliance: Does it use the exact function name and parameters?
            
            If one solution is clearly superior, select it. If multiple have strengths, synthesize a new solution combining the best parts.
            Return ONLY the final function implementation. No explanations. No markdown. Include imports if needed.""",
            contexts_list=solution_approaches
        )

        # Step 4: Validate and refine through code execution with retries
        final_code = None
        last_error = None
        
        for attempt in range(3):
            try:
                # Attempt to execute and validate the code
                execution_result = await self.programmer(
                    instruction=f"""Execute this code and validate it against the problem requirements.
                    Problem Analysis: {problem_analysis}
                    
                    Requirements for code:
                    - Must be executable Python code
                    - Must define the exact function specified
                    - Must handle edge cases
                    - Must return correct type
                    - No syntax errors or runtime exceptions""",
                    context=synthesized_solution,
                    max_retries=1
                )
                
                # If we get here, execution was successful
                final_code = synthesized_solution
                break
                
            except Exception as e:
                last_error = str(e)
                # Revise the code based on error
                synthesized_solution = await self.revise(
                    instruction=f"""Fix the code based on this error: {last_error}
                    Also ensure:
                    - Function signature is exactly as required
                    - All edge cases from analysis are handled
                    - Return type matches specification
                    - No extra text or markdown - ONLY the function implementation
                    - Include necessary imports inside the function if needed""",
                    context=synthesized_solution
                )

        # If programmer failed after retries, use the last synthesized solution
        if final_code is None:
            final_code = synthesized_solution

        # Step 5: Extract clean function implementation (remove any extra text)
        # Look for def keyword and extract until function end
        def extract_function_code(code_text):
            # Try to find the function definition
            lines = code_text.split('\n')
            in_function = False
            function_lines = []
            brace_count = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('def ') and not in_function:
                    in_function = True
                    function_lines.append(line)
                    # Count braces in this line
                    brace_count += line.count('{') - line.count('}')
                elif in_function:
                    function_lines.append(line)
                    # Count braces
                    brace_count += line.count('{') - line.count('}')
                    # If we have a return statement and brace_count is 0, we might be at the end
                    # But Python doesn't use braces, so we'll look for dedent instead
                    if stripped.startswith('return') and len(line) - len(line.lstrip()) <= len(function_lines[0]) - len(function_lines[0].lstrip()):
                        # This return is at same or lower indent than def, likely end of function
                        break
            
            if function_lines:
                return '\n'.join(function_lines)
            
            # Fallback: try regex for def...return pattern
            import re
            pattern = r'(def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*?\)\s*:.*?return\s+.*?)(?=\n\s*def|\n\s*$|\Z)'
            match = re.search(pattern, code_text, re.DOTALL)
            if match:
                return match.group(1).strip()
            
            # Last resort: return original
            return code_text.strip()

        # Clean the final code
        cleaned_code = extract_function_code(final_code)
        
        # Ensure it starts with def and has no extra wrapping
        if not cleaned_code.startswith('def '):
            # Try one last revision to get clean code
            cleaned_code = await self.revise(
                instruction="""Return ONLY the function implementation. 
                - Must start with 'def function_name(...):'
                - No markdown, no explanations, no extra text
                - Include imports if needed
                - Must be valid Python code""",
                context=final_code
            )
            
            # Final extraction attempt
            cleaned_code = extract_function_code(cleaned_code)

        return cleaned_code