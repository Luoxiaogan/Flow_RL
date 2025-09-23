# Workflow ID: humaneval_79_0
# Benchmark: humaneval
# Data Indices: [104, 21]

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

        # Step 1: Parallel analysis - decompose the problem from multiple angles
        literal_analysis = await self.generate(
            instruction="""Analyze the provided examples in the docstring with extreme precision.
            - What exact input-output transformations are demonstrated?
            - What patterns or rules can be inferred from these examples?
            - Do not extrapolate beyond what is shown, but note every detail.
            Format your response as a structured breakdown of each example.""",
            context=""
        )

        edge_analysis = await self.generate(
            instruction="""Anticipate edge cases and unstated constraints.
            - Based on the problem domain (e.g., 'digits', 'rescaling', 'lists'), what boundary conditions might exist?
            - Consider: empty inputs, single elements, extreme values, type boundaries, implicit assumptions.
            - How might the examples be misleading or incomplete?
            List and justify each potential edge case.""",
            context=""
        )

        structural_analysis = await self.generate(
            instruction="""Extract exact structural requirements.
            - What is the function name (ENTRY POINT)? Confirm it exactly.
            - What are the input and output types? Be precise (int vs float, list vs tuple, etc.).
            - Are there any explicit constraints in the docstring (e.g., 'sorted', 'at least two elements')?
            - What must the code NOT do? (e.g., no extra prints, no additional parameters)
            Provide a bullet-point specification checklist.""",
            context=""
        )

        # Step 2: Synthesize analyses into a unified spec
        unified_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into one comprehensive specification for code generation.
            - Combine the literal example mappings with edge case anticipations.
            - Incorporate structural constraints (naming, typing, etc.).
            - Prioritize correctness over elegance.
            - The spec must be detailed enough to guide unambiguous implementation.
            Format as a developer-ready spec with sections: Examples, Edge Cases, Constraints, Return Type.""",
            contexts_list=[literal_analysis, edge_analysis, structural_analysis]
        )

        # Step 3: Generate multiple candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Implement the function based EXACTLY on this spec:
                {unified_spec}

                Rules:
                - Use the exact function name from ENTRY POINT.
                - Match return types precisely (if examples show integers, return int; floats, return float).
                - Do not add any extra functionality, imports, or comments unless necessary.
                - Handle all anticipated edge cases.
                - Code must be minimal and direct.
                Return ONLY the function definition, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Implement the function with a different algorithmic approach, still adhering to:
                {unified_spec}

                Try to solve it from a different angle (e.g., if one solution uses string parsing, try math operations; if one uses loops, try comprehensions).
                Rules same as above: exact name, correct types, minimal code.
                Return ONLY the function definition.""",
                context=""
            )
        )

        # Step 4: Validate each candidate against the spec and examples
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Critique this candidate implementation:
                {candidate}

                Against the unified spec:
                {unified_spec}

                Questions to answer:
                - Does it handle all shown examples correctly?
                - Does it address the anticipated edge cases?
                - Is the function name and return type correct?
                - Are there any logical flaws or over/under-engineering?
                Be brutally honest. If flawed, explain exactly why and how to fix it.""",
                context=candidate
            ) for candidate in candidates]
        )

        # Step 5: Ensemble the best candidate or synthesize a new one
        final_code = await self.ensemble(
            instruction="""You are given candidate implementations and their critiques.
            Select the best one OR synthesize a new version that combines their strengths and fixes their flaws.
            Criteria:
            1. Must pass all shown examples (verify logic against docstring examples).
            2. Must handle key edge cases identified in analysis.
            3. Must have exact function name and return type.
            4. Must be simplest and most readable.
            Return ONLY the final function definition, nothing else. No markdown, no explanations.""",
            contexts_list=[f"Candidate:\n{candidates[i]}\n\nCritique:\n{validations[i]}" for i in range(len(candidates))]
        )

        # Step 6: Final sanitization - ensure only code is returned
        # Extract code block if present, or clean any remaining prose
        code_match = re.search(r'