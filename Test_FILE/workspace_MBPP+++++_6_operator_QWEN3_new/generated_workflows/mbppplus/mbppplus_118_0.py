# Workflow ID: mbppplus_118_0
# Benchmark: mbppplus
# Data Indices: [27, 248]

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

        # === PHASE 1: PROBLEM CHARACTERIZATION ===
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem. Extract:
            1. Primary domain (string, math, list/set, logic, etc.)
            2. Input types and constraints (e.g., 'positive integer', 'non-empty string')
            3. Output type and format requirements (e.g., 'return tuple', 'must be integer')
            4. Key operations needed (e.g., 'replace characters', 'sum prime factors')
            5. Likely edge cases (empty input, zero, negatives, duplicates, boundaries)
            6. Algorithmic patterns (iterative, recursive, mathematical formula, etc.)
            7. Any implicit constraints or assumptions
            Format as a structured JSON-like block with clear section headers.""",
            context=""
        )

        # === PHASE 2: STRATEGY GENERATION (PARALLEL) ===
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a DIRECT solution strategy:
                - Write concise pseudocode or step-by-step logic
                - Focus on simplicity and direct implementation
                - Assume standard library functions are available
                - Handle edge cases mentioned in analysis: {problem_analysis}
                - Output only the strategy steps, no explanations.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a DECOMPOSED solution strategy:
                - Break problem into 2-4 logical subproblems
                - Specify dependencies between subproblems
                - For each subproblem, describe input, output, and method
                - Ensure coverage of edge cases from: {problem_analysis}
                - Output as numbered subproblems with dependency notes.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a TEST-DRIVEN solution strategy:
                - First, list 5 critical test cases including edge cases from: {problem_analysis}
                - Then, describe solution that passes all these tests
                - Emphasize input validation and type handling
                - Output test cases first, then solution approach.""",
                context=problem_analysis
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # === PHASE 3: STRATEGY SELECTION ===
        selected_strategy = await self.ensemble(
            instruction="""Select the BEST solution strategy based on:
            1. Completeness (covers all edge cases and requirements)
            2. Clarity and implementability
            3. Efficiency and simplicity
            4. Alignment with problem constraints
            Return ONLY the selected strategy text, no commentary.""",
            contexts_list=strategy_candidates
        )

        # === PHASE 4: CODE GENERATION ===
        initial_code = await self.programmer(
            instruction=f"""Implement the solution using this strategy:
            {selected_strategy}
            
            STRICT REQUIREMENTS:
            - Use EXACT function name and signature from problem
            - Include all necessary imports inside function if needed
            - Handle all edge cases identified in analysis
            - Return correct data type (list vs tuple vs set matters)
            - No wrapper functions or classes - only the requested function
            - Code must be production-ready and pass rigorous tests""",
            context=selected_strategy,
            max_retries=3
        )

        # === PHASE 5: EDGE CASE VALIDATION ===
        edge_cases = await self.generate(
            instruction=f"""Generate 5 critical edge case test scenarios based on:
            Problem Analysis: {problem_analysis}
            Generated Code: {initial_code}
            
            For each case, specify:
            - Input value
            - Expected behavior/output
            - Why this case is critical
            Format as Python assert statements.""",
            context=initial_code
        )

        # Validate edge cases in parallel
        validation_results = []
        edge_case_lines = [line.strip() for line in edge_cases.split('\n') if line.strip().startswith('assert')]
        
        if edge_case_lines:
            validation_tasks = []
            for edge_case in edge_case_lines[:5]:  # Limit to 5 for efficiency
                validation_tasks.append(
                    self.programmer(
                        instruction=f"""Execute this edge case test on the implementation:
                        Edge case: {edge_case}
                        Code: {initial_code}
                        
                        Return 'PASS' if test passes, 'FAIL: [reason]' if fails.
                        Be strict about type matching and edge behavior.""",
                        context=f"{initial_code}\n\n{edge_case}",
                        max_retries=1
                    )
                )
            validation_results = await asyncio.gather(*validation_tasks)

        # === PHASE 6: REFINEMENT LOOP ===
        current_code = initial_code
        for iteration in range(2):  # Max 2 refinement iterations
            if all("PASS" in result.upper() for result in validation_results):
                break
                
            failure_summary = "\n".join([f"Case {i+1}: {result}" for i, result in enumerate(validation_results) if "FAIL" in result.upper()])
            
            current_code = await self.revise(
                instruction=f"""REVISE THE CODE TO FIX FAILURES:
                Current code: {current_code}
                Failure cases: {failure_summary}
                Problem analysis: {problem_analysis}
                
                REQUIRED FIXES:
                - Address all failing edge cases specifically
                - Maintain correct function signature
                - Preserve type consistency
                - Don't break existing passing cases
                - Return only the corrected function implementation""",
                context=current_code
            )
            
            # Re-validate only failed cases
            if failure_summary:
                validation_tasks = []
                for i, result in enumerate(validation_results):
                    if "FAIL" in result.upper():
                        validation_tasks.append(
                            self.programmer(
                                instruction=f"""Re-test edge case: {edge_case_lines[i] if i < len(edge_case_lines) else 'unknown'}
                                Code: {current_code}
                                Return 'PASS' or 'FAIL: [reason]'""",
                                context=f"{current_code}\n\n{edge_case_lines[i] if i < len(edge_case_lines) else ''}",
                                max_retries=1
                            )
                        )
                if validation_tasks:
                    validation_results = await asyncio.gather(*validation_tasks)

        # === PHASE 7: FORMAT EXTRACTION ===
        final_code = await self.summarize(
            instruction="""Extract ONLY the function implementation from the following code.
            Requirements:
            - Remove any markdown, explanations, or wrapper text
            - Preserve exact function signature and body
            - Include necessary imports if inside function
            - Output must be ready to execute as-is
            - If multiple functions, extract only the one matching problem signature
            
            Use regex pattern matching if needed to isolate function definition.
            Return ONLY the clean function code, nothing else.""",
            context=current_code
        )

        return final_code