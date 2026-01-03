# Workflow ID: humaneval_1_0
# Benchmark: humaneval
# Data Indices: [17, 45]

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

        # Step 1: Classify problem complexity and extract key patterns
        classification = await self.generate(
            instruction="""Analyze the problem and classify its complexity and type. Consider:
            - Is this a simple mathematical formula, a string parsing task, or a complex algorithm?
            - How many examples are provided? Do they reveal edge cases?
            - Are there explicit or implicit constraints on input/output types?
            - Does the docstring mention specific edge cases (empty input, zero, etc.)?
            - What is the expected return type (int, float, list, etc.) based on examples?
            Output a structured classification in this format:
            Complexity: [trivial|moderate|complex]
            Type: [math|string|algorithm|other]
            KeyPatterns: [bullet points of observed patterns from examples]
            EdgeCases: [list of potential edge cases inferred]
            ReturnType: [expected return type]""",
            context=""
        )

        # Step 2: Conditional branching based on complexity
        if "trivial" in classification.lower() or "simple" in classification.lower():
            # Simple path: direct generation + revision
            candidate = await self.generate(
                instruction=f"""Generate Python code for the function based on the specification and examples.
                Classification context: {classification}
                
                Instructions:
                - Implement exactly what is specified, nothing more.
                - Match return types precisely (int vs float matters).
                - Handle edge cases only if implied by examples.
                - Output ONLY the function body as a string (no signature, no imports).
                - Use clean, minimal Python code.""",
                context=""
            )
            
            final_code = await self.revise(
                instruction=f"""Critically revise the generated code:
                - Verify against each example in the docstring by mentally simulating execution.
                - Ensure return type matches examples exactly.
                - Add minimal edge case handling ONLY if clearly implied.
                - Remove any over-engineering or unnecessary complexity.
                - Output ONLY the corrected function body as a string.
                
                Classification context: {classification}""",
                context=candidate
            )
            
        else:
            # Complex path: parallel candidate generation
            candidate_instructions = [
                """Generate implementation focusing strictly on literal interpretation of docstring text.
                Ignore examples if they conflict with docstring description.
                Output ONLY function body.""",
                
                """Generate implementation by extrapolating patterns ONLY from examples, ignoring docstring text if ambiguous.
                Focus on input-output transformation patterns.
                Output ONLY function body.""",
                
                """Generate defensive implementation that explicitly handles all edge cases mentioned or implied in examples.
                Include guards for empty input, zero values, etc. if remotely plausible.
                Output ONLY function body."""
            ]
            
            # Generate candidates in parallel
            candidates = await asyncio.gather(
                *[self.generate(instruction=f"{instr}
                
                Classification context: {classification}
                
                Remember: Output ONLY the function body as a string.", context="") 
                  for instr in candidate_instructions]
            )
            
            # Ensemble: select best candidate
            selected_candidate = await self.ensemble(
                instruction=f"""Select the best implementation from the candidates below:
                - Must pass all examples in the docstring (mentally simulate each).
                - Must match return types exactly.
                - Should handle edge cases without over-engineering.
                - Prefer simplicity and directness.
                - Output ONLY the selected function body as a string.
                
                Classification context: {classification}""",
                contexts_list=candidates
            )
            
            # Revise selected candidate
            final_code = await self.revise(
                instruction=f"""Final revision pass:
                - Re-simulate ALL examples mentally. Fix any mismatches.
                - Verify return type precision (int/float/list etc.).
                - Trim any unnecessary code while preserving correctness.
                - Ensure no imports or extra code - ONLY function body.
                - Output ONLY the final function body as a string.
                
                Classification context: {classification}""",
                context=selected_candidate
            )

        return final_code