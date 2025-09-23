# Workflow ID: mbppplus_146_0
# Benchmark: mbppplus
# Data Indices: [247, 126]

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
        import math

        # Step 1: Decompose problem into solution dimensions
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into four critical dimensions:
            1. Input/Output Specification: What are the exact types and structures of inputs and outputs? 
               (e.g., list vs tuple, string encoding, numeric ranges)
            2. Algorithmic Strategy: What core algorithm or computational approach is needed? 
               (e.g., mathematical formula, string filtering, set operations)
            3. Edge Case Landscape: What are the 5 most likely edge cases based on problem domain patterns?
               (e.g., empty inputs, single elements, duplicates, extreme values, type boundaries)
            4. Implementation Constraints: What are the non-functional requirements? 
               (e.g., must preserve order, must be immutable, performance constraints, import restrictions)
            Return each dimension as a separate subproblem with clear, actionable descriptions.""",
            context=""
        )

        # Step 2: Generate parallel solution hypotheses
        hypothesis_tasks = [
            self.generate(
                instruction=f"""Generate a solution hypothesis focusing on LITERAL INTERPRETATION:
                - Implement exactly what's described without over-engineering
                - Prioritize direct mapping from problem statement to code
                - Assume minimal edge cases unless explicitly mentioned
                - Use simplest possible data structures and algorithms
                Base your hypothesis on this decomposition: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution hypothesis focusing on EDGE CASE ROBUSTNESS:
                - Assume hidden test suite contains 200+ edge cases
                - Systematically handle: empty inputs, single elements, duplicates, type boundaries, invalid inputs
                - Add defensive programming: type checks, input validation, fallback behaviors
                - Prioritize correctness over elegance
                Base your hypothesis on this decomposition: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution hypothesis focusing on CODE ELEGANCE & EFFICIENCY:
                - Use most Pythonic, concise, and readable approach
                - Leverage built-in functions and standard library optimally
                - Avoid unnecessary variables or steps
                - Consider performance implications for large inputs
                Base your hypothesis on this decomposition: {decomposition}""",
                context=""
            )
        ]
        
        hypotheses = await asyncio.gather(*hypothesis_tasks)

        # Step 3: Ensemble synthesize unified strategy
        unified_strategy = await self.ensemble(
            instruction="""Synthesize a unified implementation strategy from these three hypotheses:
            - Combine literal accuracy with edge case robustness and code elegance
            - Resolve conflicts by prioritizing: correctness > robustness > elegance
            - Explicitly state how to handle each identified edge case
            - Specify exact data types and structures for inputs/outputs
            - Include any necessary imports or library functions
            - Output should be a clear, step-by-step implementation plan ready for coding""",
            contexts_list=hypotheses
        )

        # Step 4: Generate initial code implementation
        initial_code = await self.programmer(
            instruction=f"""Generate Python code implementing the function as specified.
            Follow this strategy exactly: {unified_strategy}
            Requirements:
            - Include all necessary imports at top
            - Use exact function name and signature from problem
            - Handle all edge cases mentioned in strategy
            - Return correct data type (list/tuple/set) as specified
            - Code must be self-contained and runnable
            - Add minimal comments only if critical for clarity""",
            context=unified_strategy
        )

        # Step 5: Generate validation critique
        critique = await self.generate(
            instruction=f"""Act as a senior test engineer critiquing this code:
            - Identify 3-5 potential failure points or edge cases not handled
            - Check for type mismatches (e.g., returning list when tuple expected)
            - Verify input validation and error handling
            - Assess performance bottlenecks for large inputs
            - Flag any deviations from problem specification
            - Suggest specific improvements without rewriting code
            Code to critique: {initial_code}""",
            context=initial_code
        )

        # Step 6: Iterative revision loop (max 2 iterations)
        current_code = initial_code
        for iteration in range(2):
            if "no issues found" in critique.lower() or "perfect" in critique.lower():
                break
                
            revised_code = await self.revise(
                instruction=f"""Revise the code to address these specific issues:
                {critique}
                Requirements:
                - Fix all identified issues while preserving core functionality
                - Maintain exact function signature
                - Add necessary input validation and edge case handling
                - Keep code as concise as possible
                - Do not change algorithm unless absolutely necessary""",
                context=current_code
            )
            current_code = revised_code
            
            # Re-critique if not last iteration
            if iteration < 1:  # Only critique again if we have another revision chance
                critique = await self.generate(
                    instruction=f"""Critique this revised code:
                    - Has it fixed the previous issues?
                    - Are there any new issues introduced?
                    - Is it now robust against edge cases?
                    Code: {current_code}""",
                    context=current_code
                )

        # Step 7: Final defensive fallback if critique still shows issues
        if "issue" in critique.lower() or "error" in critique.lower() or "fail" in critique.lower():
            current_code = await self.programmer(
                instruction=f"""Generate DEFENSIVE implementation:
                - Handle ALL possible edge cases exhaustively
                - Add type checking and input validation for every parameter
                - Use try-except blocks for potential errors
                - Return safe defaults for invalid inputs
                - Prioritize robustness over performance or elegance
                - Include comprehensive error messages
                Base on original strategy: {unified_strategy}
                And address these remaining issues: {critique}""",
                context=unified_strategy
            )

        return current_code