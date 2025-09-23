# Workflow ID: humaneval_59_0
# Benchmark: humaneval
# Data Indices: [85, 18]

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
        Universal code generation workflow for function implementation from specifications.
        Uses multi-perspective analysis, synthesis, simulation-based revision, and precision filtering.
        """
        import asyncio
        import re

        # STEP 1: PARALLEL MULTI-PERSPECTIVE ANALYSIS
        # Generate three independent analytical perspectives simultaneously
        example_analysis, spec_analysis, strategy_analysis = await asyncio.gather(
            self.generate(
                instruction="""Perform example-driven reverse engineering:
                - Examine each example input-output pair in the docstring
                - Identify transformation patterns: what changes? what stays?
                - Infer implicit rules from concrete cases
                - Map inputs to outputs step by step
                - Highlight any edge cases demonstrated
                - Do NOT write code yet — focus purely on pattern extraction""",
                context=""
            ),
            self.generate(
                instruction="""Perform specification-driven contract analysis:
                - Extract all explicit requirements from docstring
                - Identify return type expectations (int, float, bool, etc.)
                - Note any mentioned edge cases or special conditions
                - List constraints (e.g., "non-empty", "positive only")
                - Clarify ambiguous terms using examples as context
                - Structure findings as bullet points for implementation""",
                context=""
            ),
            self.generate(
                instruction="""Perform strategy-driven algorithmic analysis:
                - Identify computational pattern: iteration, recursion, filtering, etc.
                - Suggest relevant algorithms or data structures
                - Consider time/space complexity implied by examples
                - Propose variable naming and loop structures
                - Reference similar classic problems if applicable
                - Outline step-by-step logic without writing full code""",
                context=""
            )
        )

        # STEP 2: SYNTHESIZE PERSPECTIVES INTO IMPLEMENTATION PLAN
        implementation_plan = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified implementation plan:
            - Reconcile any contradictions between perspectives
            - Prioritize specification requirements over inferred patterns
            - Adopt the most efficient strategy that satisfies examples
            - Explicitly state: function signature, core logic, edge case handling
            - Include exact variable names and loop conditions
            - Format as a clear, numbered implementation checklist
            - If any analysis is weak or irrelevant, disregard it gracefully""",
            contexts_list=[example_analysis, spec_analysis, strategy_analysis]
        )

        # STEP 3: GENERATE INITIAL CODE IMPLEMENTATION
        initial_code = await self.generate(
            instruction=f"""Generate Python function implementation based EXACTLY on this plan:
            {implementation_plan}

            CRITICAL REQUIREMENTS:
            - Function name MUST match ENTRY POINT exactly
            - Return type MUST match examples precisely (int vs float matters)
            - Handle all edge cases mentioned in specification
            - Code must be minimal — no extra features or comments
            - Use efficient, readable Python idioms
            - Do NOT include imports or test code — only function body
            - If examples show specific behavior (e.g., overlapping matches), replicate exactly""",
            context=implementation_plan
        )

        # STEP 4: SIMULATION-BASED REVISION LOOP (max 2 iterations)
        current_code = initial_code
        for iteration in range(2):
            validation_feedback = await self.generate(
                instruction=f"""Simulate code execution against ALL examples in docstring:
                - For each example input, mentally trace through the code line by line
                - Verify output matches expected result exactly
                - If any mismatch, identify exact line and variable causing error
                - Check edge cases: empty inputs, zeros, duplicates, boundaries
                - Also verify: correct function name, return type, no over-engineering
                - If perfect, respond 'VALIDATED'
                - If flawed, respond with specific correction instructions""",
                context=current_code
            )
            
            if "VALIDATED" in validation_feedback.upper():
                break
                
            # Revise based on simulation feedback
            current_code = await self.revise(
                instruction=f"""Apply these corrections based on example simulation:
                {validation_feedback}
                
                PRESERVE:
                - Original function signature and entry point
                - Core algorithmic approach unless fundamentally flawed
                - Minimalist style — no added complexity
                
                OUTPUT ONLY THE CORRECTED FUNCTION BODY""",
                context=current_code
            )

        # STEP 5: PRECISION FILTER — STRIP TO ESSENTIALS
        final_code = await self.summarize(
            instruction="""Extract ONLY the clean function implementation:
            - Remove any explanatory comments or markdown
            - Ensure no print statements or debug code
            - Verify function name matches ENTRY POINT exactly
            - Confirm return statement exists and matches type
            - Output nothing except the raw Python function body
            - If multiple functions exist, keep only the specified entry point""",
            context=current_code
        )

        return final_code