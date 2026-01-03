# Workflow ID: humaneval_15_0
# Benchmark: humaneval
# Data Indices: [33, 25]

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
        Uses example-driven simulation and iterative refinement to ensure correctness.
        """
        import asyncio
        import re

        # Phase 1: Extract and structure the specification from docstring
        spec_analysis = await self.generate(
            instruction="""Thoroughly analyze the function specification and examples:
            1. What is the explicit description of what the function should do?
            2. For each example, what is the exact transformation from input to output?
            3. What patterns or rules can be inferred from the examples?
            4. What edge cases might be implied (empty inputs, single elements, negatives, etc.)?
            5. What must remain unchanged vs. what must be transformed?
            6. What data types are involved and what must be preserved?
            Present your analysis in a structured, detailed format.""",
            context=""
        )

        # Phase 2: Generate multiple candidate solutions in parallel
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate a solution based STRICTLY on the literal description in the docstring.
                Ignore examples for now. Focus on implementing exactly what the text says.
                Ensure function name matches ENTRY POINT exactly.
                Return only the function body as code, no explanations.
                Analysis context: {spec_analysis}""",
                context=spec_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution by reverse-engineering ONLY from the input-output examples.
                Ignore the descriptive text. Look for patterns in how inputs transform to outputs.
                What operations, when applied, turn each input into its corresponding output?
                Implement the minimal generalization of those operations.
                Return only the function body as code, no explanations.
                Analysis context: {spec_analysis}""",
                context=spec_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution that anticipates edge cases and robustness.
                Based on the analysis, what could go wrong? Handle empty lists, single elements, 
                negative numbers, zeros, duplicates, etc. as implied by examples.
                Make the code defensive and precise.
                Return only the function body as code, no explanations.
                Analysis context: {spec_analysis}""",
                context=spec_analysis
            )
        ]
        
        initial_candidates = await asyncio.gather(*candidate_tasks)

        # Phase 3: Simulate each candidate against examples
        simulation_tasks = []
        for i, candidate in enumerate(initial_candidates):
            simulation = await self.revise(
                instruction=f"""Simulate the execution of this code against EVERY example in the docstring.
                For each example:
                1. Show the input
                2. Step through the code's execution
                3. Show the actual output
                4. Compare with expected output
                5. If mismatch, explain exactly why and how to fix it
                Be brutally honest. If it fails, say so clearly.
                Candidate {i+1}: {candidate}""",
                context=candidate
            )
            simulation_tasks.append(simulation)

        # Phase 4: Revise candidates based on simulation feedback
        revised_candidates = []
        for i, (candidate, simulation) in enumerate(zip(initial_candidates, simulation_tasks)):
            if "mismatch" in simulation.lower() or "fail" in simulation.lower() or "error" in simulation.lower():
                # Revise with specific feedback
                revised = await self.revise(
                    instruction=f"""Fix the code based on this simulation feedback:
                    {simulation}
                    
                    Errors to fix:
                    - Ensure function name matches ENTRY POINT exactly
                    - Return types must match examples precisely (int vs float, list vs tuple, etc.)
                    - Handle edge cases as implied by examples
                    - Only implement what's specified — no extras
                    Return only the corrected function body as code.""",
                    context=candidate
                )
                # One more simulation to verify fix
                verification = await self.revise(
                    instruction=f"""Re-simulate the fixed code against all examples.
                    If still failing, explain why. If passing, say 'VERIFIED'.
                    Candidate: {revised}""",
                    context=revised
                )
                if "verified" in verification.lower():
                    revised_candidates.append(revised)
                else:
                    # If still failing, keep original for ensemble to judge
                    revised_candidates.append(candidate)
            else:
                # Passed simulation, keep as is
                revised_candidates.append(candidate)

        # Phase 5: Ensemble select the best candidate
        final_code = await self.ensemble(
            instruction="""Select the BEST solution from the candidates below.
            Criteria:
            1. Must pass all example simulations (output matches exactly)
            2. Must be clean, minimal, and precise
            3. Must use correct data types (int vs float, list vs tuple, etc.)
            4. Must not over-engineer — implement exactly what's specified
            5. Function name must match ENTRY POINT exactly
            Return ONLY the selected function body as code, nothing else.
            If multiple are good, pick the most elegant and precise.""",
            contexts_list=revised_candidates
        )

        return final_code