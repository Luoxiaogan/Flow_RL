# Workflow ID: mbppplus_12_0
# Benchmark: mbppplus
# Data Indices: [246, 306, 195]

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

        # PHASE 1: PARALLEL PROBLEM DECOMPOSITION
        # Generate three orthogonal analyses concurrently
        type_analysis, algorithm_analysis, edge_case_analysis = await asyncio.gather(
            self.generate(
                instruction="""Perform deep type contract analysis:
                - Identify expected input types and structures
                - Infer output type and format requirements
                - Note any implicit type constraints or conversions
                - Flag potential type ambiguities or coercion points
                - Consider how empty/None inputs should be handled
                Output as structured bullet points with confidence levels.""",
                context=""
            ),
            self.generate(
                instruction="""Perform algorithmic strategy analysis:
                - Identify core computational pattern (filter, transform, reduce, generate, etc.)
                - Suggest 2-3 possible algorithmic approaches with complexity estimates
                - Reference similar known algorithms or patterns
                - Highlight potential performance bottlenecks
                - Note any mathematical properties or invariants that could be leveraged
                Output as numbered approaches with pros/cons.""",
                context=""
            ),
            self.generate(
                instruction="""Perform edge case taxonomy:
                - List all possible boundary conditions (empty, single element, max/min values)
                - Identify data shape variations (nested, flat, irregular)
                - Consider type edge cases (None, mixed types, unexpected structures)
                - Note domain-specific edge cases (negative numbers, zero, duplicates)
                - Flag any edge cases that might break naive implementations
                Output as categorized checklist with severity ratings.""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZED SPECIFICATION
        # Ensemble the three analyses into unified problem specification
        unified_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, coherent problem specification:
            - Resolve any contradictions between analyses (e.g., type vs edge case conflicts)
            - Prioritize edge cases by likelihood and severity
            - Select the most appropriate algorithmic approach based on type constraints and edge cases
            - Define clear success criteria for the solution
            - Output as: 1) Type Contract, 2) Algorithm Choice, 3) Edge Case Handling Requirements, 4) Validation Criteria""",
            contexts_list=[type_analysis, algorithm_analysis, edge_case_analysis]
        )

        # PHASE 3: ADVERSARIAL SOLUTION GENERATION
        # Generate minimal and defensive solutions in parallel
        minimal_solution, defensive_solution = await asyncio.gather(
            self.generate(
                instruction=f"""Generate MINIMAL solution based on specification:
                {unified_spec}
                
                Requirements:
                - Match reference solution style (concise, direct)
                - Focus on core logic only
                - Assume ideal inputs (no error handling)
                - Prioritize readability and simplicity
                - Use exact function signature from problem
                Output ONLY the function implementation with necessary imports.""",
                context=unified_spec
            ),
            self.generate(
                instruction=f"""Generate DEFENSIVE solution based on specification:
                {unified_spec}
                
                Requirements:
                - Handle all edge cases identified in specification
                - Include type checking and input validation
                - Use clear variable names and comments for complex logic
                - Prioritize robustness over brevity
                - Use exact function signature from problem
                Output ONLY the function implementation with necessary imports.""",
                context=unified_spec
            )
        )

        # PHASE 4: CROSS-REVISION & HYBRIDIZATION
        # Revise each solution using insights from the other
        refined_minimal = await self.revise(
            instruction=f"""Enhance minimal solution with defensive insights:
            - Incorporate critical edge case handling from defensive solution
            - Add minimal necessary validation without bloating code
            - Preserve elegance while increasing robustness
            - Ensure type consistency with specification
            Output ONLY the improved function implementation.""",
            context=f"Minimal Solution:\n{minimal_solution}\n\nDefensive Insights:\n{defensive_solution}"
        )

        refined_defensive = await self.revise(
            instruction=f"""Streamline defensive solution with minimal insights:
            - Remove redundant validations or over-engineering
            - Simplify complex logic where possible
            - Adopt cleaner patterns from minimal solution
            - Maintain essential edge case handling
            Output ONLY the improved function implementation.""",
            context=f"Defensive Solution:\n{defensive_solution}\n\nMinimal Insights:\n{minimal_solution}"
        )

        # PHASE 5: VALIDATION & SYNTHETIC TESTING
        # Generate synthetic test cases and validate solutions
        synthetic_tests = await self.generate(
            instruction=f"""Generate 5 synthetic test cases based on specification:
            {unified_spec}
            
            Requirements:
            - Include 2 edge cases not in original examples
            - Include 1 performance stress test (large input)
            - Include 1 type boundary case
            - Include 1 malformed input case
            - Format as Python assert statements
            Output as code block with assert statements only.""",
            context=unified_spec
        )

        validation_report = await self.generate(
            instruction=f"""Validate both solutions against synthetic tests:
            Synthetic Tests:
            {synthetic_tests}
            
            For each solution:
            - Predict which tests would pass/fail
            - Identify specific failure points
            - Suggest fixes for failing cases
            Output as structured report with solution comparison.""",
            context=f"Refined Minimal:\n{refined_minimal}\n\nRefined Defensive:\n{refined_defensive}\n\nTests:\n{synthetic_tests}"
        )

        # PHASE 6: FINAL ENSEMBLE & OUTPUT
        # Select or synthesize final solution
        final_solution = await self.ensemble(
            instruction=f"""Produce final solution based on validation:
            {validation_report}
            
            Selection Criteria:
            - Must pass all synthetic tests
            - Prefer simpler solution if both pass
            - If both fail, synthesize hybrid with necessary fixes
            - Ensure exact function signature and return type
            - Remove any debug prints or unnecessary comments
            Output ONLY the final function implementation with necessary imports.""",
            contexts_list=[refined_minimal, refined_defensive, validation_report]
        )

        return final_solution