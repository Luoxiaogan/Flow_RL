# Workflow ID: humaneval_60_0
# Benchmark: humaneval
# Data Indices: [117, 83]

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

        # Step 1: Parallel problem analysis from multiple perspectives
        analysis_promises = [
            self.generate(
                instruction="""Perform a deep algorithmic analysis of the problem:
                - Break down the required function into step-by-step operations
                - Identify input processing, core logic, and output formatting
                - Note any explicit or implicit constraints from examples
                - Suggest appropriate data structures and control flow
                - Highlight potential edge cases mentioned or implied""",
                context=""
            ),
            self.generate(
                instruction="""Perform a mathematical/formulaic analysis of the problem:
                - Look for numerical patterns in the examples
                - Determine if a closed-form solution exists
                - Identify base cases and recurrence relations
                - Consider combinatorial or probabilistic approaches
                - Express relationships as equations if possible""",
                context=""
            ),
            self.generate(
                instruction="""Perform a constraint and edge case analysis:
                - List all explicit constraints from the docstring
                - Infer implicit constraints from examples
                - Identify boundary conditions (empty inputs, single elements, etc.)
                - Note special cases that might break naive implementations
                - Consider type requirements and precision needs""",
                context=""
            )
        ]
        
        algorithmic_analysis, mathematical_analysis, constraint_analysis = await asyncio.gather(*analysis_promises)
        
        # Step 2: Synthesize analyses into unified problem understanding
        unified_understanding = await self.ensemble(
            instruction="""Synthesize the three analyses into a comprehensive problem understanding:
            - Combine algorithmic, mathematical, and constraint perspectives
            - Resolve any conflicts between analyses
            - Prioritize solution approaches based on problem characteristics
            - Create a unified list of requirements and edge cases
            - Determine the most promising solution strategy (algorithmic, mathematical, or hybrid)
            - Output should be a structured plan for implementation""",
            contexts_list=[algorithmic_analysis, mathematical_analysis, constraint_analysis]
        )
        
        # Step 3: Generate initial solution based on unified understanding
        initial_solution = await self.generate(
            instruction=f"""Generate Python code that solves the problem exactly as specified:
            - Use the function name specified in ENTRY POINT
            - Implement the solution strategy identified in the unified understanding
            - Handle all edge cases identified in constraint analysis
            - Match return types and formats shown in examples
            - Code should be clean, efficient, and readable
            - Include no extra functionality beyond what's specified
            
            Unified Understanding:
            {unified_understanding}""",
            context=unified_understanding
        )
        
        # Step 4: Validation and refinement loop (up to 3 iterations)
        current_solution = initial_solution
        for iteration in range(3):
            # Validate solution against potential edge cases
            validation = await self.generate(
                instruction=f"""Critically evaluate this solution for correctness and robustness:
                - Mentally simulate all provided examples
                - Test against identified edge cases (empty inputs, boundaries, etc.)
                - Check for off-by-one errors, type mismatches, or logical flaws
                - Verify that return types match examples exactly
                - Identify any missing constraints or special cases
                - If solution appears correct, state "NO ISSUES FOUND"
                - Otherwise, list specific issues and suggested fixes
                
                Current Solution:
                {current_solution}""",
                context=current_solution
            )
            
            # If no issues found, break out of loop
            if "NO ISSUES FOUND" in validation.upper():
                break
                
            # Otherwise, revise solution based on validation feedback
            current_solution = await self.revise(
                instruction=f"""Revise the solution to fix all identified issues:
                - Address each specific problem mentioned in validation
                - Maintain the core approach unless fundamental flaw exists
                - Ensure all edge cases are properly handled
                - Preserve correct behavior for provided examples
                - Keep code clean and focused on specification
                
                Validation Feedback:
                {validation}""",
                context=current_solution
            )
        
        # Step 5: Generate fallback brute-force solution (in parallel with final validation)
        fallback_solution, final_validation = await asyncio.gather(
            self.generate(
                instruction="""Generate a simple, brute-force solution as fallback:
                - Prioritize correctness over efficiency
                - Use straightforward loops and conditionals
                - Handle all edge cases explicitly
                - Match examples exactly
                - This is a backup in case elegant solution has hidden flaws""",
                context=""
            ),
            self.generate(
                instruction=f"""Final validation of the refined solution:
                - Confirm solution handles all examples correctly
                - Verify edge case coverage
                - Check for any remaining logical gaps
                - If confident, state "SOLUTION VALIDATED"
                - If any doubt remains, state "USE FALLBACK"
                
                Refined Solution:
                {current_solution}""",
                context=current_solution
            )
        )
        
        # Step 6: Final ensemble decision
        if "USE FALLBACK" in final_validation.upper():
            final_solution = fallback_solution
        else:
            # Even if validated, compare with fallback for robustness
            final_solution = await self.ensemble(
                instruction="""Select the most robust and correct solution:
                - Prefer solutions that handle edge cases explicitly
                - Choose the solution most likely to pass hidden test cases
                - If both are equally good, prefer the more efficient one
                - Output only the selected code, nothing else""",
                contexts_list=[current_solution, fallback_solution]
            )
        
        return final_solution