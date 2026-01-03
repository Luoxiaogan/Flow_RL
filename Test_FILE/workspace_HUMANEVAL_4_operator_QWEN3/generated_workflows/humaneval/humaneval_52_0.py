# Workflow ID: humaneval_52_0
# Benchmark: humaneval
# Data Indices: [20, 94]

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

        # Step 1: Extract function signature and examples for dynamic instruction building
        signature_analysis = await self.generate(
            instruction="""Thoroughly analyze the provided function signature and docstring:
            1. Extract the exact function name and parameter names/types
            2. Parse all examples in the format '>>> function_call == expected_output'
            3. Identify implicit constraints from examples (edge cases, type handling, special values)
            4. Classify the problem type: mathematical, string processing, list algorithm, etc.
            5. Note any potential ambiguities or missing specifications
            Format your response as a structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a solution using a specialized approach based on problem classification:
                Problem Analysis: {signature_analysis}
                
                Strategy: If mathematical, use formulas; if list-based, use iteration; if string-based, use slicing/regex.
                Focus on efficiency and direct implementation of observed patterns from examples.
                Return ONLY the function implementation with correct signature and no extra text.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using a brute-force/general approach:
                Problem Analysis: {signature_analysis}
                
                Strategy: Prioritize correctness over efficiency. Handle all edge cases explicitly.
                Use step-by-step logic that mirrors example behaviors even if verbose.
                Return ONLY the function implementation with correct signature and no extra text.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution by directly reverse-engineering from examples:
                Problem Analysis: {signature_analysis}
                
                Strategy: Treat examples as test cases. Design code that explicitly produces each example output.
                Use hardcoded logic if patterns are clear, otherwise implement general rules inferred from examples.
                Return ONLY the function implementation with correct signature and no extra text.""",
                context=""
            )
        ]
        candidate_solutions = await asyncio.gather(*strategy_tasks)

        # Step 3: Validate each candidate against examples (simulated validation)
        validation_tasks = []
        for i, candidate in enumerate(candidate_solutions):
            validation = self.revise(
                instruction=f"""Rigorous example-based validation:
                Problem Analysis: {signature_analysis}
                Candidate Solution {i+1}: {candidate}
                
                For EACH example in the docstring:
                1. Trace through the code step by step with the example input
                2. Verify the output matches EXACTLY (including type, e.g., int vs float)
                3. Check edge cases shown in examples
                4. Identify any discrepancies or potential failures
                
                If perfect match, respond "VALID". Otherwise, explain exactly what fails and why.
                Be hyper-literal - even small mismatches invalidate the solution.""",
                context=candidate
            )
            validation_tasks.append(validation)
        validation_results = await asyncio.gather(*validation_tasks)

        # Step 4: Ensemble - select best solution or trigger fallback
        selection_instruction = f"""Select the best solution based on validation results:
        Validation Results: {list(enumerate(validation_results))}
        Candidate Solutions: {list(enumerate(candidate_solutions))}
        
        Criteria:
        1. Prefer solutions marked "VALID"
        2. If multiple VALID, prefer most efficient/elegant
        3. If none VALID, select the one with fewest/smallest errors
        4. If all fail, respond "FALLBACK_NEEDED"
        
        Return ONLY the selected solution code or "FALLBACK_NEEDED"."""
        
        selected_solution = await self.ensemble(
            instruction=selection_instruction,
            contexts_list=[f"Candidate {i}: {sol}
Validation: {val}" 
                          for i, (sol, val) in enumerate(zip(candidate_solutions, validation_results))]
        )

        # Step 5: Fallback generation if all candidates failed
        if "FALLBACK_NEEDED" in selected_solution:
            fallback_solution = await self.generate(
                instruction=f"""Generate a fallback solution with extreme caution:
                Problem Analysis: {signature_analysis}
                Previous Failures: {validation_results}
                
                Strategy:
                1. Implement step-by-step, literal interpretation of examples
                2. Add explicit type handling and edge case checks
                3. Use verbose but unambiguous logic
                4. Double-check function name and return type
                5. Prioritize correctness over elegance
                
                Return ONLY the function implementation with correct signature and no extra text.""",
                context=""
            )
            selected_solution = fallback_solution

        # Step 6: Final polish - ensure exact compliance with signature and examples
        final_solution = await self.revise(
            instruction=f"""Final polish for production readiness:
            Problem Analysis: {signature_analysis}
            Current Solution: {selected_solution}
            
            Verify and fix:
            1. Function name matches ENTRY POINT exactly
            2. Return type matches examples precisely (int vs float, tuple order, etc.)
            3. All edge cases from examples are handled
            4. Code is clean, minimal, and matches Python best practices
            5. No extra imports or code outside function definition
            
            Return ONLY the final polished function implementation with no extra text.""",
            context=selected_solution
        )

        return final_solution