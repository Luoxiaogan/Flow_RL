# Workflow ID: humaneval_73_0
# Benchmark: humaneval
# Data Indices: [151, 132]

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

        # Step 1: Extract and formalize examples from docstring
        example_extraction = await self.generate(
            instruction="""Thoroughly extract all input-output examples from the docstring. 
            For each example:
            - Identify the function call and its arguments
            - Identify the expected return value
            - Note any edge cases (empty input, single element, invalid types, etc.)
            - Format as: "INPUT: ... -> OUTPUT: ..."
            Also extract any explicit constraints or special handling rules mentioned in text.
            Be meticulous — these examples are your test suite.""",
            context=""
        )

        # Step 2: Generate multiple candidate solutions in parallel
        candidate_instructions = [
            """Generate a Python function that satisfies the specification.
            Focus on literal interpretation of examples. Prioritize correctness over elegance.
            Handle edge cases explicitly. Return type must match examples exactly.
            Do NOT hardcode example values — generalize the pattern.""",
            
            """Generate a Python function focusing on robust type handling and edge cases.
            Assume inputs may contain mixed types, floats, negatives, or empty structures.
            Use defensive programming. Include explicit type checks or conversions as needed.
            Return type must be identical to examples (int vs float matters).""",
            
            """Generate a Python function using the most mathematically or logically elegant approach.
            Look for underlying patterns or formulas. Optimize for clarity and simplicity.
            Still handle all edge cases from examples. Match return type precisely."""
        ]

        candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context=example_extraction) 
              for instr in candidate_instructions]
        )

        # Step 3: Simulate each candidate against extracted examples
        simulation_tasks = []
        for i, candidate in enumerate(candidates):
            simulation = self.generate(
                instruction=f"""Simulate executing this candidate code against ALL extracted examples.
                For each example input, predict the output step-by-step.
                Compare predicted output with expected output.
                Identify any mismatches or edge cases that might fail.
                Format: "Example 1: PASSED/FAILED — Reason: ..."
                Also predict behavior on perturbed examples (e.g., if example uses [1,3,2,0], test [2,4,6]).
                Be brutally honest — even small type mismatches (int vs float) are failures.
                Candidate Code:
                {candidate}""",
                context=example_extraction
            )
            simulation_tasks.append(simulation)
        
        simulation_results = await asyncio.gather(*simulation_tasks)

        # Step 4: Ensemble select best candidate based on simulation fidelity
        best_candidate = await self.ensemble(
            instruction="""Select the candidate that best satisfies ALL examples and constraints.
            Prioritize:
            1. Correctness on all provided examples
            2. Robust handling of edge cases
            3. Return type precision (int vs float must match examples)
            4. Generalization (not hardcoded to example values)
            If multiple candidates are equally good, prefer the simplest.
            Return ONLY the selected candidate code — no explanations.""",
            contexts_list=candidates
        )

        # Step 5: Revise for precision, edge cases, and specification alignment
        refined_candidate = await self.revise(
            instruction=f"""Critically revise this code:
            - Ensure function name matches ENTRY POINT exactly
            - Verify return type matches examples precisely (int vs float)
            - Handle ALL edge cases mentioned in examples (empty input, invalid types, etc.)
            - Remove any hardcoded example values — must be general solution
            - Add minimal necessary type checks or conversions
            - Preserve core logic but harden against failure
            - Return ONLY the corrected function — no comments or explanations unless required by spec.
            Original examples for reference:
            {example_extraction}""",
            context=best_candidate
        )

        # Step 6: Final sanity check — summarize logic and cross-verify with spec
        logic_summary = await self.summarize(
            instruction="""Summarize the logic of this code in plain English.
            Then, cross-check against original specification:
            - Does it handle all cases mentioned?
            - Are there any deviations from requirements?
            - Is the return type correct?
            If any issues found, note them concisely.
            Otherwise, output 'VALID'. Code:
            """ + refined_candidate,
            context=refined_candidate
        )

        # Final output: if summary found issues, do one last revision; else return as-is
        if "VALID" not in logic_summary:
            final_output = await self.revise(
                instruction=f"""Fix any issues noted in this summary:
                {logic_summary}
                Return ONLY the corrected function.""",
                context=refined_candidate
            )
        else:
            final_output = refined_candidate

        return final_output