# Workflow ID: mbppplus_60_0
# Benchmark: mbppplus
# Data Indices: [211, 65, 334]

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

        # Phase 1: Problem Classification and Requirement Extraction
        classification = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Classify problem type: string, math, list, logic, or other.
            2. Extract exact input/output types and format requirements.
            3. Identify explicit and implicit constraints.
            4. List potential edge cases (empty inputs, boundaries, type variations).
            5. Suggest optimal solution strategy (formula, iteration, regex, etc.).
            Format as structured JSON-like text with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        # Branch 1: Specialized Strategy (based on classification)
        specialized_strategy = await self.generate(
            instruction=f"""Based on classification:
            {classification}
            
            Generate optimal solution:
            - Use domain-specific optimizations (regex for strings, formulas for math)
            - Handle identified edge cases explicitly
            - Match exact return type and function signature
            - Include necessary imports inside function if needed
            Output ONLY the function implementation as code.""",
            context=classification
        )

        # Branch 2: Brute-Force Fallback (simple, reliable)
        brute_force = await self.generate(
            instruction=f"""Generate simple, foolproof solution:
            - Use basic loops or straightforward logic
            - Prioritize correctness over elegance
            - Include defensive checks for edge cases
            - Match exact function signature and return type
            Output ONLY the function implementation as code.""",
            context=classification
        )

        # Branch 3: Adversarial Edge Case Generation
        edge_cases = await self.generate(
            instruction="""Act as adversarial tester:
            - List 5 sneaky edge cases not mentioned in problem
            - Consider: empty inputs, type mismatches, extreme values, unicode, None
            - Format as bullet points with brief justification
            - Focus on cases that would break naive implementations""",
            context=classification
        )

        # Phase 3: Ensemble Synthesis
        candidate_solutions = [specialized_strategy, brute_force]
        synthesized = await self.ensemble(
            instruction=f"""Synthesize best solution:
            - Compare candidates for correctness, efficiency, edge case handling
            - Prefer specialized approach unless edge cases invalidate it
            - Incorporate defensive checks from brute-force if missing
            - Ensure output format matches exactly (tuple vs list, etc.)
            - Use adversarial edge cases as validation checklist:
            {edge_cases}
            Output ONLY the final function implementation as code.""",
            contexts_list=candidate_solutions
        )

        # Phase 4: Iterative Refinement (max 2 iterations)
        current_solution = synthesized
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Critique this code:
                - Check for edge case vulnerabilities (especially: {edge_cases})
                - Verify type consistency and function signature
                - Look for off-by-one errors, unhandled exceptions
                - Suggest specific fixes if any issues found
                If no issues, respond 'VALID'.
                Otherwise, list issues concisely.""",
                context=current_solution
            )
            
            if "VALID" in validation.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Fix all issues:
                - Address vulnerabilities: {validation}
                - Maintain exact function signature and return type
                - Keep code clean and efficient
                - Add comments only if critical for clarity
                Output ONLY the revised function implementation.""",
                context=current_solution
            )

        # Phase 5: Final Justification Summary (internal consistency check)
        justification = await self.summarize(
            instruction="""Summarize why this solution is robust:
            - List handled edge cases
            - Confirm type/format compliance
            - Note efficiency characteristics
            - Highlight any defensive programming
            Keep under 100 words.""",
            context=current_solution
        )

        return current_solution