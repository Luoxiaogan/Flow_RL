# Workflow ID: humaneval_76_0
# Benchmark: humaneval
# Data Indices: [55, 157]

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
        Universal workflow for code generation from docstring specifications.
        Handles edge cases, return type inference, and hidden test simulation.
        """
        import asyncio
        import re

        # Stage 1: Specification Analysis
        spec_analysis = await self.generate(
            instruction="""Perform deep structural analysis of the problem:
            1. Extract function signature and parameter types
            2. List all provided examples with inputs and expected outputs
            3. Infer the problem domain (mathematical, logical, string, etc.)
            4. Identify potential edge cases (zero, negative, empty, boundary values)
            5. Determine expected return type (int, float, bool, etc.) from examples
            6. Note any constraints or implicit assumptions
            Format as structured JSON with keys: signature, examples, domain, edge_cases, return_type, constraints""",
            context=""
        )

        # Stage 2: Pattern Inference
        pattern_inference = await self.revise(
            instruction=f"""Given the specification analysis:
            {spec_analysis}

            Infer the underlying algorithm or mathematical principle:
            - For numerical problems: identify recurrence relations, formulas, or patterns
            - For logical problems: deduce decision rules or conditions
            - For string problems: determine transformation rules or regex patterns
            - For geometric problems: apply relevant theorems or identities
            Also consider:
            - Time/space complexity constraints (if any)
            - Potential off-by-one errors
            - Type coercion requirements
            Output as detailed reasoning with clear algorithmic steps""",
            context=spec_analysis
        )

        # Stage 3: Parallel Code Drafting (Generate 3 variants)
        draft_instructions = [
            "Implement the solution using a recursive approach. Handle base cases explicitly.",
            "Implement the solution using an iterative approach. Optimize for clarity and efficiency.",
            "Implement the solution using mathematical formulas or built-in operations where possible."
        ]

        code_drafts = await asyncio.gather(*[
            self.generate(
                instruction=f"""{instr}
                - Use the exact function name from the specification
                - Match return types precisely (int vs float matters)
                - Handle all edge cases identified in analysis
                - Include no imports unless absolutely necessary
                - Return only the function definition (no test code or explanations)
                Base your implementation on this pattern inference:
                {pattern_inference}""",
                context=""
            ) for instr in draft_instructions
        ])

        # Stage 4: Validation Simulation
        simulated_tests = await self.generate(
            instruction=f"""Generate 5 simulated test cases that would likely be in the hidden test suite:
            - Include edge cases identified in specification analysis
            - Cover boundary conditions
            - Test type sensitivity (int vs float)
            - Include at least one 'tricky' case that might break naive implementations
            Format as Python assert statements, one per line""",
            context=spec_analysis
        )

        # Simulate each draft against simulated tests
        simulation_results = []
        for i, draft in enumerate(code_drafts):
            simulation = await self.generate(
                instruction=f"""Simulate executing this code draft:
                {draft}
                
                Against these test cases:
                {simulated_tests}
                
                For each test case:
                1. Predict the output
                2. Note if it matches expected result
                3. Identify any failures or type mismatches
                4. Suggest fixes if needed
                Return structured report with pass/fail status for each test""",
                context=draft
            )
            simulation_results.append(simulation)

        # Stage 5: Targeted Revision
        revised_drafts = []
        for i, (draft, sim_result) in enumerate(zip(code_drafts, simulation_results)):
            if "fail" in sim_result.lower() or "error" in sim_result.lower():
                revised = await self.revise(
                    instruction=f"""Revise this code draft:
                    {draft}
                    
                    It failed these simulated tests:
                    {sim_result}
                    
                    Fix the issues while:
                    - Preserving correctness on original examples
                    - Maintaining the exact function signature
                    - Matching return types precisely
                    - Not introducing new bugs
                    Return only the corrected function definition""",
                    context=draft
                )
                revised_drafts.append(revised)
            else:
                revised_drafts.append(draft)  # No revision needed

        # Stage 6: Final Synthesis
        final_code = await self.ensemble(
            instruction="""Select the best implementation from the candidates below:
            Criteria:
            1. Correctness (passes all simulated tests)
            2. Simplicity (minimal, readable code)
            3. Efficiency (optimal time/space complexity)
            4. Robustness (handles edge cases)
            5. Adherence to specification (exact function name, return types)
            If multiple candidates are equally good, prefer the most straightforward implementation.
            Return ONLY the selected function definition (no explanations or markdown)""",
            contexts_list=revised_drafts
        )

        return final_code