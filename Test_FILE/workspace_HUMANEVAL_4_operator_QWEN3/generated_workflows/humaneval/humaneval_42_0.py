# Workflow ID: humaneval_42_0
# Benchmark: humaneval
# Data Indices: [69, 15]

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

        # Step 1: Extract function name from ENTRY POINT
        extract_name_instr = """
        From the original problem, locate the section labeled "ENTRY POINT: Function name: [name]".
        Extract ONLY the function name as a plain string. Do not include any explanations, markdown, or code.
        Example: If it says "Function name: search", return "search".
        """
        function_name = await self.generate(instruction=extract_name_instr, context="")

        # Step 2: Analyze specification and extract constraints
        analyze_instr = f"""
        Analyze the function specification and examples. Extract:
        1. Input type and structure
        2. Output type and format (be precise: int, str, list, etc.)
        3. Key constraints or conditions (e.g., "greater than zero", "frequency >= value")
        4. Edge cases implied by examples (empty? single element? all fail condition?)
        5. Algorithmic hints from input-output pairs
        
        Format as a structured summary with clear section headers.
        """
        spec_analysis = await self.generate(instruction=analyze_instr, context="")

        # Step 3: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """
            Propose a BRUTE FORCE solution strategy.
            - Iterate through all possible candidates
            - Check condition for each
            - Return first/last valid or default
            - Simple, readable, no optimizations
            """,
            """
            Propose an OPTIMIZED solution strategy.
            - Use data structures for efficiency (dict, set, etc.)
            - Minimize passes over data
            - Leverage mathematical insights if possible
            - Consider space-time tradeoffs
            """,
            """
            Propose a DECLARATIVE solution strategy.
            - Use comprehensions, built-ins, functional style
            - Focus on readability and conciseness
            - Avoid explicit loops if possible
            - Pythonic and idiomatic
            """
        ]

        strategy_tasks = [
            self.generate(instruction=instr, context=spec_analysis)
            for instr in strategy_instructions
        ]
        strategies = await asyncio.gather(*strategy_tasks)

        # Step 4: Ensemble - evaluate and select best strategy
        ensemble_instr = f"""
        Evaluate these {len(strategies)} solution strategies against the specification:

        SPECIFICATION:
        {spec_analysis}

        CRITERIA:
        1. Correctness: Must handle all example cases and implied edge cases
        2. Simplicity: Minimal, no over-engineering
        3. Efficiency: Reasonable for problem scale
        4. Precision: Matches return type exactly
        5. Robustness: No hidden assumptions

        For each strategy, simulate execution on provided examples.
        Select the SINGLE BEST strategy. Return ONLY the selected strategy text.
        """
        selected_strategy = await self.ensemble(
            instruction=ensemble_instr,
            contexts_list=strategies
        )

        # Step 5: Generate algorithmic pseudocode
        pseudocode_instr = f"""
        Convert the selected strategy into step-by-step pseudocode:
        - Use clear, imperative steps
        - Include initialization, iteration, condition checks, return statements
        - Handle edge cases explicitly
        - Match return type precisely (int, str, etc.)
        - Do NOT write actual Python code yet

        Strategy to convert:
        {selected_strategy}
        """
        pseudocode = await self.generate(instruction=pseudocode_instr, context="")

        # Step 6: Revise pseudocode against examples
        revise_pseudo_instr = f"""
        Validate this pseudocode against ALL provided examples in the specification.
        For each example:
        1. Trace through the pseudocode step by step
        2. Verify output matches expected result
        3. Check edge cases (empty, single element, all invalid, etc.)
        4. Ensure return type is correct

        If any discrepancy, revise the pseudocode to fix it.
        Return the corrected pseudocode.
        """
        validated_pseudocode = await self.revise(
            instruction=revise_pseudo_instr,
            context=pseudocode
        )

        # Step 7: Generate final Python code
        code_gen_instr = f"""
        Convert this pseudocode into Python code:
        - Function name MUST be: {function_name.strip()}
        - Match return type exactly as specified (int, str, etc.)
        - Handle all edge cases identified in analysis
        - Use minimal, clean code - no comments, no extra imports
        - No over-engineering - implement exactly what's needed
        - Return the code as a raw string without markdown or explanations

        Pseudocode:
        {validated_pseudocode}
        """
        code = await self.generate(instruction=code_gen_instr, context="")

        # Step 8: Final revision for syntax and precision
        final_revise_instr = f"""
        Review this code for:
        1. Exact function name: must be "{function_name.strip()}"
        2. Return type precision: must match examples (int vs float vs str)
        3. Syntax correctness: no missing colons, brackets, etc.
        4. Edge case handling: as identified in specification analysis
        5. Minimalism: remove any unnecessary code or imports

        Return ONLY the corrected Python code as a raw string.
        """
        final_code = await self.revise(instruction=final_revise_instr, context=code)

        return final_code