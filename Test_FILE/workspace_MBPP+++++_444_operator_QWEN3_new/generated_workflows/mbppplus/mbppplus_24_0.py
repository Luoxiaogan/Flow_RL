# Workflow ID: mbppplus_24_0
# Benchmark: mbppplus
# Data Indices: [245, 235, 186]

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
        import json

        # Phase 1: Parallel Problem Analysis
        problem_analysis, spec_extraction = await asyncio.gather(
            self.generate(
                instruction="""Thoroughly classify this programming problem by:
                1. Identifying the core algorithmic archetype (greedy, dynamic programming, regex, set operations, etc.)
                2. Determining the primary data structures involved (arrays, strings, trees, etc.)
                3. Recognizing any mathematical or logical patterns
                4. Estimating complexity constraints (if any)
                5. Suggesting 2-3 standard algorithms or approaches that could apply
                Format as a structured JSON with keys: "archetype", "data_structures", "patterns", "algorithms".""",
                context=""
            ),
            self.generate(
                instruction="""Extract precise output specifications by:
                1. Analyzing test cases to infer return type (int, str, list, etc.)
                2. Identifying edge case requirements (empty inputs, single elements, duplicates)
                3. Noting any formatting constraints (exact string matches, specific variable names)
                4. Detecting hidden constraints from assertion patterns
                Format as structured JSON with keys: "return_type", "edge_cases", "formatting", "constraints".""",
                context=""
            )
        )

        # Phase 2: Triple-Strategy Solution Generation
        direct_approach, formal_approach, brute_force_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution by direct translation:
                - If reference solution exists, mimic its structure while improving clarity
                - If no reference, implement the most straightforward approach
                - Use exact function signature from problem
                - Include necessary imports
                - Handle edge cases identified in spec: {spec_extraction}
                Return ONLY the function implementation as code.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using formal algorithms:
                - Apply textbook algorithms matching the archetype: {problem_analysis}
                - Optimize for correctness over brevity
                - Include detailed comments explaining algorithm choice
                - Ensure type consistency with spec: {spec_extraction}
                Return ONLY the function implementation as code.""",
                context=spec_extraction
            ),
            self.generate(
                instruction=f"""Generate a brute-force solution with insight:
                - Start with naive approach, then add optimizations
                - Focus on edge case robustness from spec: {spec_extraction}
                - Include assertions for key edge cases
                - Use clear variable names reflecting problem domain
                Return ONLY the function implementation as code.""",
                context=problem_analysis + "\n" + spec_extraction
            )
        )

        # Phase 3: Ensemble Synthesis with Discrepancy Detection
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution by:
            1. Comparing logic across all three approaches
            2. Resolving discrepancies through majority vote or correctness priority
            3. Preserving edge-case handling from brute-force approach
            4. Maintaining efficiency from formal approach
            5. Ensuring code clarity from direct approach
            6. Verifying return type and signature match problem requirements
            Return ONLY the final function implementation as code.""",
            contexts_list=[direct_approach, formal_approach, brute_force_approach]
        )

        # Phase 4: Iterative Edge-Case Validation
        for _ in range(3):  # Maximum 3 revision cycles
            edge_cases = await self.generate(
                instruction=f"""Generate 5 challenging edge cases for this problem:
                - Include empty inputs, single elements, duplicates, boundary values
                - Consider type mismatches, extreme values, and malformed data
                - Format as Python assert statements
                Based on problem analysis: {problem_analysis} and spec: {spec_extraction}""",
                context=synthesized_solution
            )
            
            validation = await self.generate(
                instruction=f"""Critically validate the solution against these edge cases:
                {edge_cases}
                1. Identify any failures or weaknesses
                2. Suggest specific code revisions
                3. Prioritize fixes by severity
                Return detailed revision instructions or 'PASSED' if no issues.""",
                context=synthesized_solution
            )
            
            if "PASSED" in validation.upper():
                break
                
            synthesized_solution = await self.revise(
                instruction=f"""Revise the solution to fix all identified issues:
                {validation}
                1. Maintain exact function signature
                2. Preserve existing correct functionality
                3. Add comments for each fix
                Return ONLY the revised function implementation as code.""",
                context=synthesized_solution
            )

        # Phase 5: Type and Signature Conformance
        final_solution = await self.revise(
            instruction="""Ensure strict conformance to problem requirements:
            1. Verify function name and parameter names match exactly
            2. Confirm return type matches extracted specifications
            3. Include all necessary imports at top of function
            4. Remove any debug prints or extra outputs
            5. Format code with proper indentation and spacing
            Return ONLY the final function implementation as code.""",
            context=synthesized_solution
        )

        return final_solution