# Workflow ID: mbppplus_6_0
# Benchmark: mbppplus
# Data Indices: [286, 70, 164]

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

        # Phase 1: Parallel Hypothesis Generation
        # Generate three independent solution perspectives simultaneously
        direct_impl, edge_validator, math_reform = await asyncio.gather(
            self.generate(
                instruction="""Generate a direct Python implementation based strictly on the problem description.
                Focus on clarity and simplicity. Assume standard inputs unless specified otherwise.
                Include type hints in comments if helpful. Do NOT copy reference solution verbatim.
                Handle obvious edge cases (empty, zero, single element) even if not mentioned.
                Return ONLY the function code with necessary imports inside the function if needed.""",
                context=""
            ),
            self.generate(
                instruction="""Act as an adversarial tester. Your goal is to BREAK the solution.
                Generate a comprehensive list of edge cases, failure modes, and stress tests.
                Consider: negative numbers, zero, floating points, empty inputs, single elements, 
                duplicates, type mismatches, overflow, and boundary conditions.
                For each case, explain WHY it might break a naive implementation and HOW to fix it.
                Format as bullet points with clear categorization.""",
                context=""
            ),
            self.generate(
                instruction="""Re-derive the solution from first principles. Ignore the reference solution.
                If mathematical: show derivation steps. If logical: show truth tables or state transitions.
                If algorithmic: describe the invariant and termination condition.
                Then translate this derivation into clean Python code.
                This should be theoretically sound even if less practical.""",
                context=""
            )
        )

        # Phase 2: Cross-Informed Revision
        # Each stream revises itself using insights from the others
        revised_direct = await self.revise(
            instruction=f"""Improve this implementation using insights from the validator and reformulation:
            VALIDATOR INSIGHTS:
            {edge_validator}

            REFORMULATION INSIGHTS:
            {math_reform}

            Specific requirements:
            - Fix all edge cases mentioned by validator
            - Incorporate theoretical rigor from reformulation
            - Preserve exact function signature and return types
            - Add minimal defensive checks only where necessary
            - Keep code readable and efficient
            - Return ONLY the function code with imports if needed""",
            context=direct_impl
        )

        revised_validator = await self.revise(
            instruction=f"""Enhance this validator using the direct implementation and reformulation:
            CURRENT IMPLEMENTATION:
            {direct_impl}

            REFORMULATION:
            {math_reform}

            Improve by:
            - Adding edge cases specific to the actual implementation
            - Removing redundant or impossible cases
            - Prioritizing tests by likelihood and severity
            - Suggesting concrete code fixes for each vulnerability""",
            context=edge_validator
        )

        # Phase 3: Synthesis Ensemble
        final_code = await self.ensemble(
            instruction="""Synthesize the best elements from all revised components into one robust solution.
            Selection criteria:
            1. Correctness: Must handle all edge cases from validator
            2. Efficiency: Prefer O(1) over O(n) when possible without sacrificing clarity
            3. Readability: Clean, well-named variables, minimal complexity
            4. Type Safety: Exact return types as specified in signature
            5. Minimalism: No unnecessary imports or defensive checks

            Take structure from direct implementation, robustness from validator, 
            and theoretical soundness from reformulation.
            Return ONLY the final function code with necessary imports inside.""",
            contexts_list=[revised_direct, revised_validator, math_reform]
        )

        # Phase 4: Adversarial Stress Test & Final Polish
        stress_test = await self.generate(
            instruction=f"""Generate 5 pathological test cases designed to break this solution:
            {final_code}
            
            Focus on:
            - Extreme values (sys.maxsize, -sys.maxsize-1)
            - Type coercion edge cases
            - Floating point precision issues
            - Empty/None inputs if applicable
            - Unicode/string edge cases for string problems
            Return as Python assert statements.""",
            context=final_code
        )

        final_polish = await self.revise(
            instruction=f"""Harden the solution against these stress tests:
            {stress_test}

            Requirements:
            - Add minimal, targeted defenses only for demonstrated vulnerabilities
            - Never degrade performance for common cases
            - Maintain exact function signature
            - Keep code clean and readable
            - Return ONLY the function code with imports if needed""",
            context=final_code
        )

        # Phase 5: Confidence Assessment & Optional Deep Dive
        confidence = await self.generate(
            instruction=f"""Rate this solution's robustness on scale 1-10 with justification:
            {final_polish}
            
            Consider:
            - Coverage of edge cases
            - Theoretical soundness
            - Code clarity
            - Efficiency
            - Type safety
            Return ONLY the number (1-10) followed by brief justification.""",
            context=final_polish
        )

        # Extract confidence score
        confidence_score = int(re.search(r'^(\d+)', confidence.strip()).group(1)) if re.search(r'^(\d+)', confidence.strip()) else 5

        # Conditional deep dive for low-confidence solutions
        if confidence_score < 9:
            deep_analysis = await self.generate(
                instruction=f"""Perform deep forensic analysis of potential failure modes.
                Assume this code will be tested with 1000+ edge cases.
                Identify every possible weakness, no matter how unlikely.
                Propose surgical fixes that don't compromise performance or readability.
                Return as bullet points with code snippets for fixes.""",
                context=final_polish
            )
            
            final_polish = await self.revise(
                instruction=f"""Implement only the most critical fixes from this analysis:
                {deep_analysis}
                
                Rules:
                - Only add defenses for HIGH probability or HIGH impact issues
                - Never add more than 3 lines of defensive code
                - Preserve existing structure and readability
                - Return ONLY the function code with imports if needed""",
                context=final_polish
            )

        return final_polish