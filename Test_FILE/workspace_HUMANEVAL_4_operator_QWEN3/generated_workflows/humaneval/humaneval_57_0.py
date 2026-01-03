# Workflow ID: humaneval_57_0
# Benchmark: humaneval
# Data Indices: [95, 84]

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
        Universal workflow for Python function generation from specifications.
        Uses parallel analysis, iterative refinement, and ensemble synthesis.
        """
        import asyncio

        # PHASE 1: PARALLEL PROBLEM DECOMPOSITION
        # Generate three orthogonal analyses simultaneously
        pattern_analysis, constraint_analysis, structure_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze the examples in the docstring to identify the core pattern or transformation.
                - What is the input-to-output mapping?
                - Are there mathematical, logical, or string operations involved?
                - What changes between examples? What stays the same?
                - Express the pattern as a general rule or formula.
                Output only the pattern analysis, no code yet.""",
                context=""
            ),
            self.generate(
                instruction="""Extract ALL constraints and edge cases from the docstring and function signature.
                - What are the exact input/output types? (int, float, str, bool, etc.)
                - What edge cases are demonstrated? (empty inputs, zero, None, mixed types)
                - What must the function name be? (critical for ENTRY POINT)
                - Are there any hidden constraints? (e.g., "return False if empty")
                - List each constraint explicitly in bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Create a structural blueprint for the function.
                - What parameters does it take? What are their expected types?
                - What control flow is needed? (if/else, loops, recursion)
                - Where should early returns happen? (for edge cases)
                - What helper functions or built-ins might be useful?
                - Outline the function structure without implementing details.
                Format as: 'Function Structure: [outline]'""",
                context=""
            )
        )

        # PHASE 2: ITERATIVE REFINEMENT WITH SELF-CRITIQUE
        refined_analyses = []
        for initial_analysis in [pattern_analysis, constraint_analysis, structure_analysis]:
            current = initial_analysis
            for iteration in range(3):  # Max 3 refinement iterations
                critique = await self.generate(
                    instruction=f"""Critically evaluate this analysis against the original problem:
                    - Does it handle ALL examples shown in the docstring?
                    - Are edge cases properly addressed?
                    - Is the function naming requirement respected?
                    - Is there any over-engineering (adding features not specified)?
                    - Are return types exactly as demonstrated in examples?
                    If no issues found, respond with 'VALID'. Otherwise, list specific improvements needed.""",
                    context=current
                )
                
                if "VALID" in critique.upper():
                    break
                
                current = await self.revise(
                    instruction=f"""Revise the analysis based on this critique:
                    {critique}
                    
                    Requirements:
                    - Maintain focus on what's explicitly specified
                    - Handle all demonstrated edge cases
                    - Preserve exact function naming
                    - Match return types precisely
                    - No additional features beyond specification""",
                    context=current
                )
            refined_analyses.append(current)

        # PHASE 3: ENSEMBLE SYNTHESIS
        final_code = await self.ensemble(
            instruction="""Synthesize the best elements from all three analyses into a complete Python function.
            Requirements:
            - Use the exact function name specified in ENTRY POINT
            - Handle all edge cases identified in constraint analysis
            - Implement the core pattern from pattern analysis
            - Follow the structure from structure analysis
            - Return types must match examples exactly (int vs float matters)
            - No imports unless absolutely necessary (they'll be auto-added)
            - Output ONLY the function code, no explanations or markdown
            
            Resolve conflicts by:
            - Preferring solutions that handle more edge cases
            - Choosing stricter type adherence
            - Selecting clearer, more direct implementations
            - Ensuring no over-engineering""",
            contexts_list=refined_analyses
        )

        # FINAL CLEANUP: Ensure pure code output
        cleaned_code = await self.summarize(
            instruction="""Extract ONLY the Python function code from the text.
            - Remove any markdown code blocks (