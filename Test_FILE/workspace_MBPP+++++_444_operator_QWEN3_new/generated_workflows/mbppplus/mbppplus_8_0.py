# Workflow ID: mbppplus_8_0
# Benchmark: mbppplus
# Data Indices: [183, 209, 273]

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

        # PHASE 1: STRUCTURAL DECOMPOSITION
        decomposition = await self.generate(
            instruction="""You are a senior software engineer performing requirements analysis. 
            Extract from the problem text:
            1. The exact function signature (name, parameters, return type if inferable)
            2. The core algorithmic task in plain English
            3. All explicit and implicit constraints (edge cases, input types, output format)
            4. Any hints from test cases about expected behavior
            5. Potential failure modes (what could go wrong?)
            Format as a structured markdown list with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION DRAFTING
        draft_tasks = [
            self.generate(
                instruction=f"""Draft A: Literal Implementation
                Based on the decomposition:
                {decomposition}
                
                Write the most straightforward implementation that mirrors the reference solution style if detectable.
                Prioritize clarity and direct translation of requirements.
                Do not add defensive checks unless explicitly required.
                Return ONLY the function code with necessary imports inside the function.""",
                context=""
            ),
            self.generate(
                instruction=f"""Draft B: Defensive Implementation
                Based on the decomposition:
                {decomposition}
                
                Write a robust implementation that handles all edge cases explicitly.
                Add input validation, type checks, and boundary condition handling.
                Assume the worst possible inputs (empty, None, extreme values).
                Return ONLY the function code with necessary imports inside the function.""",
                context=""
            ),
            self.generate(
                instruction=f"""Draft C: Idiomatic Implementation
                Based on the decomposition:
                {decomposition}
                
                Write the most Pythonic, efficient implementation using built-ins, comprehensions, or itertools if appropriate.
                Prioritize elegance and performance while maintaining correctness.
                Return ONLY the function code with necessary imports inside the function.""",
                context=""
            )
        ]
        
        draft_a, draft_b, draft_c = await asyncio.gather(*draft_tasks)

        # PHASE 3: ADVERSARIAL VALIDATION
        validation_tasks = [
            self.revise(
                instruction="""You are a skeptical code reviewer. Assume this solution is flawed.
                Find the minimal input that would break it. If none exists, explain why it's robust.
                Focus on: edge cases, type mismatches, off-by-one errors, empty inputs, performance traps.
                Return your critique as a bulleted list of vulnerabilities or 'VERIFIED: No flaws found'.""",
                context=draft_a
            ),
            self.revise(
                instruction="""You are a skeptical code reviewer. Assume this solution is flawed.
                Find the minimal input that would break it. If none exists, explain why it's robust.
                Focus on: edge cases, type mismatches, off-by-one errors, empty inputs, performance traps.
                Return your critique as a bulleted list of vulnerabilities or 'VERIFIED: No flaws found'.""",
                context=draft_b
            ),
            self.revise(
                instruction="""You are a skeptical code reviewer. Assume this solution is flawed.
                Find the minimal input that would break it. If none exists, explain why it's robust.
                Focus on: edge cases, type mismatches, off-by-one errors, empty inputs, performance traps.
                Return your critique as a bulleted list of vulnerabilities or 'VERIFIED: No flaws found'.""",
                context=draft_c
            )
        ]
        
        validation_a, validation_b, validation_c = await asyncio.gather(*validation_tasks)

        # PHASE 4: SYNTHESIS AND REFINEMENT
        synthesis = await self.ensemble(
            instruction=f"""You are a principal engineer selecting the final solution.
            Given three drafts and their adversarial validations:
            
            DRAFT A:
            {draft_a}
            VALIDATION: {validation_a}
            
            DRAFT B:
            {draft_b}
            VALIDATION: {validation_b}
            
            DRAFT C:
            {draft_c}
            VALIDATION: {validation_c}
            
            Choose the solution most likely to pass ALL hidden test cases.
            Prioritize correctness over elegance. If multiple are correct, choose the simplest.
            If all have flaws, synthesize a new version combining their strengths.
            Return ONLY the final function code with necessary imports inside the function.""",
            contexts_list=[draft_a, draft_b, draft_c]
        )

        # PHASE 5: FORMAT ENFORCEMENT
        final_code = await self.revise(
            instruction="""You are a strict code formatter.
            Rewrite this solution to EXACTLY match required output format:
            - Function name and parameters must match reference exactly
            - All imports must be inside the function, at the top
            - Return type must match test case expectations
            - No extra text, comments, or docstrings unless present in reference
            - Preserve all logic but enforce syntactic compliance
            Return ONLY the formatted function code.""",
            context=synthesis
        )

        return final_code