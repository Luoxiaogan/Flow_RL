# Workflow ID: mbppplus_74_0
# Benchmark: mbppplus
# Data Indices: [326, 39, 281]

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

        # Phase 1: Decompose - Extract problem structure and classify
        decomposition = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Your output must be a JSON-like schema with these keys:
            - "problem_type": One of ["tree_algorithm", "string_manipulation", "mathematical_formula", "data_structure_operation", "logical_validation"]
            - "input_types": List of expected input types (e.g., ["Node", "List[str]", "int, int"])
            - "output_type": Expected return type (e.g., "int", "str", "List[int]")
            - "edge_cases": List of 5-7 potential edge cases (e.g., "empty input", "null root", "negative numbers")
            - "key_operations": List of core operations needed (e.g., "recursive traversal", "regex substitution", "arithmetic calculation")
            - "constraints": Any explicit or implicit constraints from the problem text
            Be exhaustive and precise. This schema will drive all subsequent steps.""",
            context=""
        )

        # Phase 2: Strategize - Generate multiple solution approaches in parallel
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using RECURSIVE/ALGORITHMIC approach.
                Problem analysis: {decomposition}
                - Use recursion if applicable
                - Handle base cases explicitly
                - Include type annotations if possible
                - Return EXACTLY the required output type
                Output ONLY the function implementation, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using ITERATIVE/PROCEDURAL approach.
                Problem analysis: {decomposition}
                - Use loops instead of recursion where possible
                - Include explicit edge case handling
                - Optimize for readability
                - Return EXACTLY the required output type
                Output ONLY the function implementation, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using BUILT-IN/UTILITARIAN approach (using Python libraries).
                Problem analysis: {decomposition}
                - Leverage Python built-ins (re, math, collections, etc.)
                - Prioritize conciseness
                - Include necessary imports
                - Return EXACTLY the required output type
                Output ONLY the function implementation, no explanations.""",
                context=""
            )
        )

        # Phase 3: Ensemble - Synthesize best solution from approaches
        synthesized_solution = await self.ensemble(
            instruction="""You are given 3 candidate solutions to the same problem. Your task:
            1. Compare them for correctness, efficiency, and edge-case coverage
            2. Synthesize a single optimal solution that:
               - Uses the most appropriate algorithmic approach
               - Handles all edge cases mentioned in the problem analysis
               - Returns the correct data type
               - Is clean and readable
               - Includes necessary imports
            3. Output ONLY the final function implementation in the required format.
            Do NOT include any explanations, markdown, or extra text.""",
            contexts_list=solution_approaches
        )

        # Phase 4: Fortify - Iteratively harden against edge cases
        hardened_solution = synthesized_solution
        for _ in range(3):  # Maximum 3 refinement cycles
            edge_case_analysis = await self.generate(
                instruction=f"""Given this solution:
                {hardened_solution}
                
                And this problem analysis:
                {decomposition}
                
                Generate 3 NEW edge cases not yet handled, then revise the code to handle them.
                Output ONLY the revised function implementation. No explanations.""",
                context=hardened_solution
            )
            
            # Only update if the revision actually changed the code
            if edge_case_analysis.strip() != hardened_solution.strip():
                hardened_solution = edge_case_analysis
            else:
                break  # No new edge cases found - exit early

        # Final cleanup: Ensure output is pure function code
        final_code = await self.revise(
            instruction="""Extract ONLY the function implementation from this text.
            - Remove any markdown code fences
            - Remove any explanatory text
            - Ensure imports are included if needed
            - Preserve exact function signature
            - Output nothing else - just the raw code""",
            context=hardened_solution
        )

        return final_code