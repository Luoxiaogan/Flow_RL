# Workflow ID: mbppplus_32_0
# Benchmark: mbppplus
# Data Indices: [233, 77, 260]

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

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: Problem Schema Extraction
        problem_schema = await self.generate(
            instruction="""Perform deep problem analysis. Extract and structure:
            1. Input types and constraints (e.g., integer n, list of strings)
            2. Expected output format and type (e.g., 2D list, string, filtered list)
            3. Key algorithmic patterns (e.g., spiral traversal, filtering, transformation)
            4. Edge cases (empty inputs, single elements, zeros, negatives)
            5. Order sensitivity and duplication handling
            6. Performance or space constraints (if any)
            Format as a structured markdown section with clear headers.""",
            context=""
        )

        # PHASE 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate IMPERATIVE strategy:
                Based on problem schema:
                {problem_schema}
                
                Design step-by-step procedural logic with:
                - State variables and their initialization
                - Loop structures and termination conditions
                - Index management and boundary handling
                - Edge case integration points
                Output as commented pseudocode with clear phases.""",
                context=problem_schema
            ),
            self.generate(
                instruction=f"""Generate FUNCTIONAL strategy:
                Based on problem schema:
                {problem_schema}
                
                Design using functional paradigms:
                - Map/filter/reduce operations
                - Lambda expressions or comprehensions
                - Built-in method exploitation (e.g., replace, Counter)
                - Recursion if applicable
                Output as high-level functional pseudocode with type annotations.""",
                context=problem_schema
            ),
            self.generate(
                instruction=f"""Generate OPTIMIZED BUILTIN strategy:
                Based on problem schema:
                {problem_schema}
                
                Identify if Python built-ins or standard library can solve 80%+:
                - String methods (replace, split, join)
                - Collections (Counter, defaultdict)
                - List comprehensions or slicing
                - Math or itertools modules
                Output as minimal pseudocode leveraging existing tools.""",
                context=problem_schema
            )
        ]
        
        strategies = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Strategy Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize optimal approach:
            Evaluate all three strategies for:
            1. Correctness coverage (edge cases, type handling)
            2. Code simplicity and readability
            3. Efficiency (time/space complexity)
            4. Robustness to input variations
            
            MERGE the best elements into one unified strategy.
            If one approach clearly dominates (e.g., built-ins for string problems), select it.
            Justify your synthesis decision in 2-3 sentences.
            Output final strategy as executable pseudocode with clear steps.""",
            contexts_list=strategies
        )

        # PHASE 4: Initial Code Generation
        initial_code = await self.generate(
            instruction=f"""Generate Python implementation:
            Using synthesized strategy:
            {synthesized_strategy}
            
            Requirements:
            - Exact function signature from problem
            - Handle ALL edge cases mentioned in schema
            - Include necessary imports at top
            - Return correct data type (list/tuple/set)
            - No external libraries unless standard
            - Add minimal comments for complex logic
            Output ONLY the function code, nothing else.""",
            context=synthesized_strategy
        )

        # PHASE 5: Code Refinement Loop
        current_code = initial_code
        for iteration in range(2):  # Max 2 refinement cycles
            refined_code = await self.revise(
                instruction=f"""Audit and fix code:
                Check for:
                1. Edge case handling (empty, single element, zeros)
                2. Correct return type matching problem spec
                3. Variable initialization and scope
                4. Loop boundaries and termination
                5. Import statements for used modules
                6. Type consistency (list vs tuple vs set)
                
                If any uncertainty or potential failure, flag with 'REVIEW_NEEDED'.
                Otherwise, output corrected code with fixes applied.
                Preserve function signature exactly.""",
                context=current_code
            )
            
            # Early termination if no issues found
            if "REVIEW_NEEDED" not in refined_code and "uncertain" not in refined_code.lower():
                current_code = refined_code
                break
                
            current_code = refined_code

        # PHASE 6: Test Simulation & Final Validation
        test_cases = await self.generate(
            instruction=f"""Generate comprehensive test cases:
            Based on problem schema:
            {problem_schema}
            
            Create 5 test cases including:
            1. Typical case (from examples)
            2. Empty input case
            3. Single element/boundary case
            4. Duplicate elements case (if applicable)
            5. Maximum/minimum value case
            Format as Python assert statements.""",
            context=problem_schema
        )

        final_code = await self.revise(
            instruction=f"""Final validation:
            Given code:
            {current_code}
            
            And test cases:
            {test_cases}
            
            Mentally simulate execution for each test case.
            Identify any mismatches or failures.
            Apply final fixes to handle all cases.
            Ensure imports are complete and return types exact.
            Output final code ready for submission.""",
            context=f"{current_code}\n\nTEST CASES:\n{test_cases}"
        )

        # PHASE 7: Uncertainty Check & Reset Branch
        if "REVIEW_NEEDED" in final_code or "uncertain" in final_code.lower():
            # Trigger reset with alternative paradigm
            reset_strategy = await self.generate(
                instruction=f"""RESET STRATEGY:
                Previous approach failed validation.
                Generate completely different solution paradigm:
                - If previous was imperative, try recursive
                - If functional, try mathematical
                - If built-in, try algorithmic from scratch
                Output as fresh pseudocode with edge case focus.""",
                context=problem_schema
            )
            
            reset_code = await self.generate(
                instruction=f"""Generate reset implementation:
                Using new strategy:
                {reset_strategy}
                
                Ignore previous attempts. Start fresh.
                Handle all edge cases from schema.
                Output complete function code with imports.""",
                context=reset_strategy
            )
            
            return reset_code

        return final_code