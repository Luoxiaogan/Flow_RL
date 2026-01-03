# Workflow ID: mbppplus_54_0
# Benchmark: mbppplus
# Data Indices: [163, 109, 26]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for programming problem-solving domain.
        Adapts strategy based on problem characteristics and self-validates for robustness.
        """
        import asyncio
        import re

        # PHASE 1: Problem Diagnosis & Classification
        diagnosis = await self.generate(
            instruction="""Perform deep problem analysis. Identify:
            1. Primary domain (string, math, list/tuple, logic, etc.)
            2. Input/output types and structures
            3. Key operations needed (search, count, transform, etc.)
            4. Edge cases to consider (empty, single element, duplicates, boundaries)
            5. Constraints (order preservation, type requirements, etc.)
            6. Similar problem patterns from reference examples
            Structure your response with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on diagnosis: {diagnosis[:1000]}
                Generate 3 distinct solution approaches. For each:
                - Describe algorithmic strategy
                - Note time/space complexity
                - Identify potential failure points
                - Suggest test cases to validate""",
                context=""
            ),
            self.generate(
                instruction=f"""Extract all explicit and implicit constraints from problem:
                {diagnosis[:1000]}
                Format as bullet points with severity levels (Critical/Important/Optional).
                Include data type requirements, edge cases, and behavioral expectations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Python function skeleton based on:
                {diagnosis[:1000]}
                Include correct function signature, parameter names, and return type.
                Add placeholder comments for key logic sections.
                Focus on structural correctness first.""",
                context=""
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)
        solution_strategies, constraints, skeleton = strategy_results

        # PHASE 3: Solution Synthesis & Ensemble
        candidate_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Implement complete solution using approach 1 from:
                {solution_strategies[:800]}
                Constraints: {constraints[:500]}
                Start from skeleton: {skeleton[:500]}
                Include edge case handling and type consistency.
                Return ONLY the function implementation with imports.""",
                context=""
            ),
            self.generate(
                instruction=f"""Implement complete solution using approach 2 from:
                {solution_strategies[:800]}
                Constraints: {constraints[:500]}
                Start from skeleton: {skeleton[:500]}
                Include edge case handling and type consistency.
                Return ONLY the function implementation with imports.""",
                context=""
            )
        )

        # PHASE 4: Solution Validation & Selection
        selected_solution = await self.ensemble(
            instruction="""Select the most robust solution. Criteria:
            1. Correctly handles all identified edge cases
            2. Matches expected input/output types
            3. Efficient and readable implementation
            4. Follows problem constraints precisely
            5. Minimal assumptions about input validity
            Justify your selection with specific comparisons.""",
            contexts_list=candidate_solutions
        )

        # PHASE 5: Robustness Audit & Refinement
        audited_solution = await self.revise(
            instruction=f"""Perform rigorous robustness audit:
            1. Verify empty input handling
            2. Check type consistency (list/tuple/set/string)
            3. Validate boundary conditions
            4. Ensure no off-by-one errors
            5. Confirm return type matches requirements
            6. Test against common failure patterns
            If any issues found, fix them while preserving core logic.
            Return ONLY the corrected function implementation.""",
            context=selected_solution
        )

        # PHASE 6: Final Formatting & Extraction
        final_solution = await self.revise(
            instruction="""Extract ONLY the Python function implementation.
            Remove all explanatory text, markdown, or additional commentary.
            Ensure:
            - Exact function signature as specified
            - All necessary imports at top
            - No wrapper functions or classes
            - Return appropriate data types
            - Clean, minimal code with no extra whitespace
            Output must be ready for direct execution.""",
            context=audited_solution
        )

        return final_solution