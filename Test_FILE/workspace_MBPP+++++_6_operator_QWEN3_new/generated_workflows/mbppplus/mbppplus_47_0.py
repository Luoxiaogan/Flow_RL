# Workflow ID: mbppplus_47_0
# Benchmark: mbppplus
# Data Indices: [163, 215]

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

        # Phase 1: Problem Decomposition
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into core components:
            1. Identify the exact input type(s) and output type(s) required.
            2. List all explicit and implicit constraints (e.g., handling empty inputs, type boundaries).
            3. Extract key operations needed (e.g., counting, filtering, transforming).
            4. Identify potential edge cases (empty, single element, duplicates, type mismatches).
            5. Note any format requirements (tuple vs list vs set, order preservation).
            Return structured subproblems with dependencies.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        solution_instructions = [
            """Generate a minimal, efficient solution focusing on core logic.
            Prioritize simplicity and speed. Assume standard inputs but include basic type checks.
            Use clear variable names and avoid unnecessary complexity.
            Return ONLY the function implementation with necessary imports.""",
            
            """Generate a robust solution with exhaustive edge case handling.
            Explicitly handle: empty inputs, single elements, invalid types, boundary values.
            Include defensive checks and clear error handling where appropriate.
            Return ONLY the function implementation with necessary imports.""",
            
            """Generate a strictly compliant solution focused on type and format correctness.
            Ensure exact return types match requirements (tuple vs list vs set).
            Preserve order if required. Handle all data type conversions explicitly.
            Return ONLY the function implementation with necessary imports."""
        ]

        # Inject decomposition context into each instruction
        decomposition_summary = "\n".join([f"{item['id']}: {item['description']}" for item in decomposition])
        enhanced_instructions = [
            f"""Based on problem decomposition:
            {decomposition_summary}

            {instr}"""
            for instr in solution_instructions
        ]

        # Generate solutions in parallel
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in enhanced_instructions]
        )

        # Phase 3: Adversarial Validation (Parallel)
        adversarial_instructions = [
            f"""Act as an adversarial tester. Assume this solution is flawed.
            Find the minimal input that would cause it to fail. Consider:
            - Type coercion issues
            - Off-by-one errors
            - Mutability assumptions
            - Boundary conditions
            - Empty/single element edge cases
            - Unicode/encoding issues (for string problems)
            - Precision/rounding (for math problems)
            Return a concise vulnerability report. If no flaws found, state "No critical vulnerabilities detected".""",
            f"""Act as an adversarial tester. Assume this solution is flawed.
            Find the minimal input that would cause it to fail. Consider:
            - Type coercion issues
            - Off-by-one errors
            - Mutability assumptions
            - Boundary conditions
            - Empty/single element edge cases
            - Unicode/encoding issues (for string problems)
            - Precision/rounding (for math problems)
            Return a concise vulnerability report. If no flaws found, state "No critical vulnerabilities detected".""",
            f"""Act as an adversarial tester. Assume this solution is flawed.
            Find the minimal input that would cause it to fail. Consider:
            - Type coercion issues
            - Off-by-one errors
            - Mutability assumptions
            - Boundary conditions
            - Empty/single element edge cases
            - Unicode/encoding issues (for string problems)
            - Precision/rounding (for math problems)
            Return a concise vulnerability report. If no flaws found, state "No critical vulnerabilities detected"."""
        ]

        vulnerability_reports = await asyncio.gather(
            *[self.revise(instruction=instr, context=sol) 
              for instr, sol in zip(adversarial_instructions, solution_attempts)]
        )

        # Phase 4: Ensemble Synthesis
        synthesis_instruction = f"""Select the best solution based on vulnerability reports:
        - Prioritize solutions with "No critical vulnerabilities detected"
        - If all have vulnerabilities, choose the one with least severe flaws
        - Synthesize a new solution if needed, combining strengths and patching weaknesses
        - Ensure final solution handles all edge cases identified in decomposition
        - Maintain exact function signature and return type requirements
        Return ONLY the final function implementation with necessary imports."""

        final_solution = await self.ensemble(
            instruction=synthesis_instruction,
            contexts_list=[f"Solution: {sol}\nVulnerabilities: {vuln}" 
                          for sol, vuln in zip(solution_attempts, vulnerability_reports)]
        )

        # Phase 5: Programmatic Verification with Iterative Fallback
        max_retries = 2
        current_solution = final_solution
        
        for attempt in range(max_retries + 1):
            try:
                # Extract test cases from problem text if available
                test_cases = []
                if "assert" in self.problem_text:
                    # Simple extraction of test cases (could be enhanced)
                    lines = self.problem_text.split('\n')
                    test_lines = [line.strip() for line in lines if line.strip().startswith('assert')]
                    test_cases = test_lines[:3]  # Use first 3 for verification
                
                verification_instruction = f"""Execute this code against test cases:
                {chr(10).join(test_cases) if test_cases else 'No explicit test cases provided - perform basic syntax and type checking.'}
                If any test fails, return detailed failure information.
                If all tests pass or no tests provided, return the code as final.
                Do NOT modify the code - only execute and report results."""
                
                verification_result = await self.programmer(
                    instruction=verification_instruction,
                    context=current_solution,
                    max_retries=1
                )
                
                # Check if verification passed (simplified check - could be enhanced)
                if "error" not in verification_result.lower() and "fail" not in verification_result.lower():
                    return current_solution
                else:
                    # Revise based on failure
                    revise_instruction = f"""The following code failed verification:
                    {verification_result}
                    
                    Revise the function to fix these specific failures while preserving core logic.
                    Handle the failing test cases explicitly.
                    Return ONLY the revised function implementation with necessary imports."""
                    
                    current_solution = await self.revise(
                        instruction=revise_instruction,
                        context=current_solution
                    )
                    
            except Exception as e:
                # If programmer fails, attempt revision with error info
                revise_instruction = f"""Code execution failed with error:
                {str(e)}
                
                Revise the function to prevent this error.
                Return ONLY the revised function implementation with necessary imports."""
                
                current_solution = await self.revise(
                    instruction=revise_instruction,
                    context=current_solution
                )

        # Return best attempt after all retries
        return current_solution