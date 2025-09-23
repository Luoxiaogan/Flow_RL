# Workflow ID: humaneval_39_0
# Benchmark: humaneval
# Data Indices: [37, 146]

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
        Universal code generation workflow that handles any specification-driven
        function implementation problem by combining spec analysis, parallel
        hypothesis generation, ensemble selection, and targeted revision.
        """
        import asyncio
        import re

        # STEP 1: Deep specification analysis - extract constraints, patterns, edge cases
        spec_analysis = await self.generate(
            instruction="""Perform deep analysis of the function specification:
            1. Identify the exact transformation required (what changes, what stays same)
            2. Extract all constraints from docstring examples (types, lengths, edge cases)
            3. List implicit edge cases not shown but likely to exist (empty input, single element, negatives, zeros)
            4. Note return type and structure requirements (must match examples exactly)
            5. Identify potential ambiguities in the specification that need resolution
            6. Determine if this is a filtering, mapping, sorting, or algorithmic problem
            Present your analysis in structured format with clear sections.""",
            context=""
        )

        # STEP 2: Generate initial solution candidate
        initial_candidate = await self.generate(
            instruction=f"""Based on this specification analysis:
            {spec_analysis}
            
            Generate Python code that implements the required function.
            CRITICAL REQUIREMENTS:
            - Function name must match ENTRY POINT exactly
            - Return type and structure must match examples precisely
            - Handle all edge cases identified in analysis
            - Code must be self-contained (no external dependencies beyond built-ins)
            - Include no explanations or comments - only raw code
            - Do not include test cases or print statements
            Generate the code now.""",
            context=spec_analysis
        )

        # STEP 3: Validate initial candidate against docstring examples (simulate check)
        validation = await self.generate(
            instruction=f"""You are a code validator. Given this code:
            {initial_candidate}
            
            And the original specification with examples, simulate execution on ALL provided examples.
            For each example:
            1. Predict the output
            2. Compare with expected output from docstring
            3. Note any mismatches or type errors
            4. Identify specific lines causing errors if any
            Return "VALID" if all examples pass, otherwise return detailed error report.""",
            context=initial_candidate
        )

        # STEP 4: Conditional branch - if valid, return; else generate parallel hypotheses
        if "VALID" in validation and len(validation) < 20:  # Simple validity check
            final_code = initial_candidate
        else:
            # Generate 3 parallel hypotheses with different interpretations
            hypotheses = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate Solution Hypothesis A:
                    Focus on literal interpretation of specification.
                    {spec_analysis}
                    Handle edge cases conservatively.
                    Code only - no explanations.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Generate Solution Hypothesis B:
                    Consider alternative interpretations of ambiguous parts.
                    {spec_analysis}
                    Be creative about edge case handling.
                    Code only - no explanations.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Generate Solution Hypothesis C:
                    Optimize for simplicity and clarity.
                    {spec_analysis}
                    Prioritize readability over cleverness.
                    Code only - no explanations.""",
                    context=""
                )
            )

            # STEP 5: Ensemble selection with reasoning
            selected_candidate = await self.ensemble(
                instruction=f"""You are selecting the best solution from 3 hypotheses.
                CRITERIA:
                1. Must pass all docstring examples when simulated
                2. Must handle edge cases identified in spec analysis
                3. Must have correct return type and structure
                4. Prefer simpler, more readable code when all else equal
                5. If none perfect, select the one with fewest/fixed errors
                Provide detailed reasoning for your selection, then output ONLY the selected code.""",
                contexts_list=hypotheses
            )

            # STEP 6: Targeted revision based on ensemble reasoning
            final_code = await self.revise(
                instruction=f"""Revise this code based on ensemble selection reasoning:
                {selected_candidate}
                
                Fix any remaining issues identified in validation or ensemble reasoning.
                Ensure:
                - Function name matches ENTRY POINT exactly
                - Return type matches examples precisely
                - All edge cases handled
                - No unnecessary complexity
                Output ONLY the final code - no explanations or comments.""",
                context=selected_candidate
            )

        # STEP 7: Final sanitization - ensure only code is returned
        code_only = await self.generate(
            instruction="""Extract ONLY the Python code from the following text.
            Remove any explanations, reasoning, markdown, or non-code text.
            Return pure Python code that can be executed directly.
            If no code found, return empty string.""",
            context=final_code
        )

        return code_only