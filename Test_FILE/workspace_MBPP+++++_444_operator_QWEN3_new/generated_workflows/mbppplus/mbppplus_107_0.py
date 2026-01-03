# Workflow ID: mbppplus_107_0
# Benchmark: mbppplus
# Data Indices: [122, 254, 53]

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

        # Phase 1: Extract Contract Specification
        contract_spec = await self.generate(
            instruction="""Perform deep contract analysis of this programming problem. Extract:
            1. EXACT input parameter types and constraints (e.g., "list of integers", "positive float")
            2. EXACT output type and format requirements (e.g., "must return tuple", "must be integer")
            3. Key edge case categories to handle (empty inputs, single elements, duplicates, negatives, type boundaries)
            4. Behavioral invariants (what must always be true about the output)
            5. Any implicit assumptions in the problem statement
            Format as structured bullet points with clear headers.""",
            context=""
        )

        # Phase 2: Parallel Candidate Generation + Test Case Generation
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate a Python solution based on this contract:
                {contract_spec}
                
                Approach 1: Literal/Reference Style - Mimic the reference solution's algorithmic approach if discernible, otherwise use most straightforward implementation.
                Include example usage with edge cases.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python solution based on this contract:
                {contract_spec}
                
                Approach 2: Idiomatic Python - Use most Pythonic, readable approach with built-ins and standard library.
                Include example usage with edge cases.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python solution based on this contract:
                {contract_spec}
                
                Approach 3: Algorithmic/Mathematical - Use mathematical insights or algorithmic optimizations.
                Include example usage with edge cases.""",
                context=""
            )
        ]
        
        # Parallel test case generation
        test_case_task = self.generate(
            instruction=f"""Generate 5 comprehensive test cases based on this contract:
            {contract_spec}
            
            Include:
            - Happy path (normal inputs)
            - Edge cases (empty, single element, duplicates, negatives, zeros, large numbers)
            - Type boundary cases
            - Potential failure modes
            Format as Python assert statements.""",
            context=""
        )

        # Execute in parallel
        candidates_and_tests = await asyncio.gather(*candidate_tasks, test_case_task)
        candidates = candidates_and_tests[:3]
        synthetic_tests = candidates_and_tests[3]

        # Phase 3: Validation and Conditional Refinement
        validation_results = []
        refined_candidates = []
        
        for i, candidate in enumerate(candidates):
            # Validate each candidate against synthetic tests (conceptually)
            validation = await self.generate(
                instruction=f"""Critically evaluate this solution against the contract and test cases:
                CONTRACT: {contract_spec}
                TEST CASES: {synthetic_tests}
                SOLUTION: {candidate}
                
                Check:
                1. Does it handle all edge cases from contract?
                2. Does output type match exactly?
                3. Are there any logical flaws or off-by-one errors?
                4. Is it robust against invalid inputs (if contract requires)?
                Return "PASSED" if flawless, otherwise detailed failure reasons.""",
                context=candidate
            )
            
            validation_results.append(validation)
            
            # Conditional refinement loop (max 2 iterations)
            current_candidate = candidate
            for attempt in range(2):
                if "PASSED" in validation.upper() and "FAILED" not in validation.upper():
                    break
                current_candidate = await self.revise(
                    instruction=f"""Revise this solution to fix the following issues:
                    {validation}
                    
                    Contract requirements: {contract_spec}
                    Maintain core logic but ensure robustness.
                    Include handling for all edge cases mentioned in contract.""",
                    context=current_candidate
                )
                # Re-validate
                validation = await self.generate(
                    instruction=f"""Re-evaluate revised solution:
                    CONTRACT: {contract_spec}
                    TEST CASES: {synthetic_tests}
                    SOLUTION: {current_candidate}
                    Return "PASSED" if fixed, otherwise new failure reasons.""",
                    context=current_candidate
                )
            
            refined_candidates.append(current_candidate)

        # Phase 4: Ensemble Selection
        final_selection = await self.ensemble(
            instruction=f"""Select the BEST solution from candidates below. Criteria:
            1. Correctness: Must handle all edge cases from contract {contract_spec}
            2. Robustness: Graceful handling of invalid inputs if required
            3. Readability: Clean, Pythonic code
            4. Efficiency: Reasonable algorithmic complexity
            If multiple correct, prefer most readable. Extract ONLY the function code.
            
            Candidates with validation results:
            {list(zip(refined_candidates, validation_results))}""",
            contexts_list=refined_candidates
        )

        # Phase 5: Code Extraction and Cleanup
        clean_code = await self.revise(
            instruction="""Extract ONLY the Python function implementation. Rules:
            - Remove all markdown, explanations, and prose
            - Keep ONLY function definition with exact signature
            - Include necessary imports at top
            - Preserve type consistency (list vs tuple vs set)
            - No wrapper functions or classes
            - Return raw code ready for execution""",
            context=final_selection
        )

        # Final sanitization: remove any remaining markdown or prose
        code_lines = []
        in_code_block = False
        for line in clean_code.split('\n'):
            if line.strip().startswith('