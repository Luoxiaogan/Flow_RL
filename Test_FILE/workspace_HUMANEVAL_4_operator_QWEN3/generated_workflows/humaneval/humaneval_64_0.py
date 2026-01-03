# Workflow ID: humaneval_64_0
# Benchmark: humaneval
# Data Indices: [3, 162]

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

        # PHASE 1: PROBLEM DISCOVERY - Extract core requirements and edge cases
        discovery = await self.generate(
            instruction="""Perform deep problem analysis. Extract:
            1. Exact function signature and ENTRY POINT name (MUST match precisely)
            2. Input type and structure (List[int], str, etc.)
            3. Expected output type and format (bool, int, str, None, etc.)
            4. All edge cases implied by examples (empty input, zeros, boundaries)
            5. Termination conditions (early return? full traversal?)
            6. Hidden constraints (type precision, performance, side effects)
            7. Step-by-step walkthrough of each example to infer algorithm
            Format as structured markdown with clear sections.""",
            context=""
        )

        # PHASE 2: STRATEGY GENERATION - Propose multiple solution approaches
        strategy_instructions = [
            """Generate Strategy 1: Imperative approach.
            - Use explicit loops and state variables
            - Early termination when condition met
            - Handle edge cases explicitly
            - Include detailed comments explaining each step
            - Justify variable names and loop conditions""",
            
            """Generate Strategy 2: Functional/declarative approach.
            - Use built-in functions (map, filter, itertools, etc.)
            - Avoid explicit loops where possible
            - Focus on readability and Pythonic style
            - Include reasoning for functional choices
            - Handle edge cases through functional composition""",
            
            """Generate Strategy 3: Mathematical/formula-based approach.
            - Look for patterns or mathematical shortcuts
            - Use cumulative operations or running calculations
            - Optimize for minimal state tracking
            - Include derivation of any formulas used
            - Justify why this approach is optimal"""
        ]

        # Generate multiple solution strategies in parallel
        strategy_candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context=discovery) 
              for instr in strategy_instructions]
        )

        # PHASE 3: CODE IMPLEMENTATION - Convert strategies to executable code
        implementation_instructions = [
            f"""Convert this strategy to executable Python code:
            {strategy}
            
            CRITICAL REQUIREMENTS:
            - Function name MUST exactly match ENTRY POINT
            - Return type MUST match examples precisely (int vs float matters)
            - Handle ALL edge cases identified in discovery phase
            - Include no imports (they'll be added automatically)
            - Code must be minimal - implement exactly what's specified
            - Add inline comments explaining key decisions
            - Ensure early termination where appropriate""",
            f"""Convert this strategy to executable Python code:
            {strategy_candidates[1]}
            
            CRITICAL REQUIREMENTS:
            - Function name MUST exactly match ENTRY POINT
            - Return type MUST match examples precisely (int vs float matters)
            - Handle ALL edge cases identified in discovery phase
            - Include no imports (they'll be added automatically)
            - Code must be minimal - implement exactly what's specified
            - Add inline comments explaining key decisions
            - Ensure early termination where appropriate""",
            f"""Convert this strategy to executable Python code:
            {strategy_candidates[2]}
            
            CRITICAL REQUIREMENTS:
            - Function name MUST exactly match ENTRY POINT
            - Return type MUST match examples precisely (int vs float matters)
            - Handle ALL edge cases identified in discovery phase
            - Include no imports (they'll be added automatically)
            - Code must be minimal - implement exactly what's specified
            - Add inline comments explaining key decisions
            - Ensure early termination where appropriate"""
        ]

        code_candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context="") 
              for instr in implementation_instructions]
        )

        # PHASE 4: VALIDATION SYNTHESIS - Critique and merge best solutions
        final_code = await self.ensemble(
            instruction="""Synthesize the best solution from these candidates:
            CRITERIA:
            1. Correctness: Must pass all examples in docstring
            2. Edge case handling: Must address all discovered edge cases
            3. Precision: Return type and function name must be exact
            4. Efficiency: Early termination where possible
            5. Minimalism: No unnecessary code or over-engineering
            6. Readability: Clear variable names and logical flow
            
            For each candidate:
            - Trace execution step-by-step on provided examples
            - Verify edge case handling
            - Check return type precision
            - Identify any flaws or improvements needed
            
            Then create a FINAL SOLUTION that:
            - Combines the strongest elements of all candidates
            - Fixes any identified flaws
            - Is production-ready and minimal
            - Includes only necessary code (no extra imports or comments unless critical)""",
            contexts_list=code_candidates
        )

        # PHASE 5: FINAL REFINEMENT - Ensure perfect compliance
        refined_code = await self.revise(
            instruction="""Final polish and compliance check:
            1. Verify function name EXACTLY matches ENTRY POINT (case-sensitive)
            2. Ensure return types match examples precisely (int vs float, None vs empty string)
            3. Confirm all edge cases from discovery phase are handled
            4. Remove any unnecessary comments or debug code
            5. Ensure minimal implementation - nothing extra
            6. Fix any off-by-one errors or boundary condition issues
            7. Validate early termination logic where applicable
            8. Return ONLY the final code with no additional text or explanations""",
            context=final_code
        )

        return refined_code