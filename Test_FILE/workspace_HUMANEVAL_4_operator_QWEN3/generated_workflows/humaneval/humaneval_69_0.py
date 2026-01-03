# Workflow ID: humaneval_69_0
# Benchmark: humaneval
# Data Indices: [100, 124]

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

        # Phase 1: Problem Deconstruction
        deconstruction = await self.generate(
            instruction="""Perform deep problem analysis. Extract and structure:
1. EXACT function name from 'ENTRY POINT' (critical for correctness)
2. Input parameter types and expected return type from examples
3. Edge cases implied by examples or specification
4. Problem domain classification: mathematical, string, validation, algorithmic, or other
5. Key constraints: format rules, range limits, special conditions
6. Solution strategy hints from examples (e.g., sequences, patterns, parsing rules)
Output as structured bullet points. Be meticulous — missing details cause test failures.""",
            context=""
        )

        # Phase 2: Parallel Hypothesis Generation
        math_hypothesis = self.generate(
            instruction=f"""Generate a solution using mathematical/algorithmic approach:
- Look for formulas, sequences, or closed-form expressions
- Use list comprehensions or generators if applicable
- Ensure return type matches examples exactly (int vs float matters)
- Handle edge cases identified in deconstruction: {deconstruction}
- Return ONLY the function definition as code, no explanations""",
            context=deconstruction
        )
        
        imperative_hypothesis = self.generate(
            instruction=f"""Generate a solution using imperative/procedural approach:
- Use explicit loops, conditionals, step-by-step construction
- Prioritize readability and direct translation of problem description
- Handle edge cases identified in deconstruction: {deconstruction}
- Ensure no over-engineering — implement exactly what's specified
- Return ONLY the function definition as code, no explanations""",
            context=deconstruction
        )
        
        functional_hypothesis = self.generate(
            instruction=f"""Generate a solution using functional/declarative approach:
- Use built-in functions, mapping, filtering, or recursion if natural
- Favor concise, expressive code while maintaining correctness
- Handle edge cases identified in deconstruction: {deconstruction}
- Match examples' return types precisely
- Return ONLY the function definition as code, no explanations""",
            context=deconstruction
        )

        hypotheses = await asyncio.gather(math_hypothesis, imperative_hypothesis, functional_hypothesis)

        # Phase 3: Critique and Gap Analysis
        critiques = await asyncio.gather(*[
            self.revise(
                instruction=f"""Critique this solution without fixing it. Analyze:
1. Does it match the ENTRY POINT function name exactly?
2. Do outputs for example inputs match docstring examples?
3. Are edge cases from deconstruction handled? If not, which ones?
4. Is return type consistent (int/float/list/etc.) with examples?
5. Any over-engineering? (e.g., unnecessary imports, extra features)
6. Potential off-by-one errors or boundary condition misses
Output as numbered critique points. Be brutally honest.""",
                context=hyp
            ) for hyp in hypotheses
        ])

        # Phase 4: Ensemble Synthesis
        annotated_hypotheses = [f"Solution:\n{hyp}\n\nCritique:\n{crit}" 
                              for hyp, crit in zip(hypotheses, critiques)]
        
        synthesized = await self.ensemble(
            instruction="""Synthesize the best solution by:
1. Selecting the most correct and concise approach
2. Merging strengths: e.g., take formula from math approach but edge-case handling from imperative
3. Ensuring function name matches ENTRY POINT exactly
4. Verifying return types match examples precisely
5. Removing any over-engineering or unnecessary complexity
6. Output ONLY the final function definition as clean code, no explanations or comments""",
            contexts_list=annotated_hypotheses
        )

        # Phase 5: Iterative Validation and Refinement (up to 2 iterations)
        current_solution = synthesized
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Mentally simulate test cases. Check:
1. For each example in docstring, does output match exactly?
2. For edge cases mentioned in deconstruction, does it handle them?
3. Any type mismatches? (e.g., returning float when example shows int)
4. Any obvious bugs? (e.g., off-by-one, unhandled formats)
5. Does function name match ENTRY POINT exactly?
If perfect, output 'VALID'. Otherwise, describe specific fixes needed.""",
                context=f"Deconstruction: {deconstruction}\n\nCurrent Solution:\n{current_solution}"
            )
            
            if "VALID" in validation.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Fix the solution based on validation feedback:
Validation Feedback: {validation}
Deconstruction Context: {deconstruction}
Rules:
- Preserve correct parts
- Fix only identified issues
- Maintain minimalism — no added features
- Ensure exact function name and return types
Output ONLY the corrected function definition as code.""",
                context=current_solution
            )

        # Phase 6: Minimalist Finalization
        final_code = await self.summarize(
            instruction="""Return ONLY the function definition as clean, minimal code.
- Remove any comments, explanations, or extra text
- Ensure exact function name from ENTRY POINT
- Match return types precisely as in examples
- No imports unless absolutely necessary (problem will auto-add)
- No extra whitespace or formatting — just the function""",
            context=current_solution
        )

        return final_code