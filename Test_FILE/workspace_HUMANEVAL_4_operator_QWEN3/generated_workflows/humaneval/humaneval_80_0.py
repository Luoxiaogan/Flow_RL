# Workflow ID: humaneval_80_0
# Benchmark: humaneval
# Data Indices: [135, 111]

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
        Universal code generation workflow for specification-driven function implementation.
        Dynamically adapts to problem structure through parallel analysis and iterative refinement.
        """
        import asyncio
        import re

        # PHASE 1: PARALLEL PROBLEM DECOMPOSITION
        # Extract multiple perspectives simultaneously
        decomposition_tasks = [
            self.generate(
                instruction="""Analyze the provided examples in the docstring with extreme precision.
                1. List every input-output pair explicitly.
                2. Identify the exact data types of inputs and outputs.
                3. Note any edge cases (empty inputs, single elements, boundary conditions).
                4. Infer the core transformation pattern from examples.
                5. Document any constraints mentioned in the natural language description.
                Format as structured markdown with clear section headers.""",
                context=""
            ),
            self.generate(
                instruction="""Extract the exact function signature and naming requirements.
                1. Identify the function name from ENTRY POINT (MUST match exactly).
                2. Note parameter names and count.
                3. Infer expected return type from examples (int, float, dict, list, etc.).
                4. Document any type constraints or validation requirements.
                Present as bullet-point checklist with 'MUST' emphasis on naming.""",
                context=""
            ),
            self.generate(
                instruction="""Translate the natural language description into algorithmic pseudocode.
                1. Break down the description into discrete steps.
                2. Identify key operations (comparison, counting, indexing, etc.).
                3. Map operations to potential Python constructs (loops, conditionals, built-ins).
                4. Note any special conditions or exceptions mentioned.
                Output as numbered steps with Python-like syntax where possible.""",
                context=""
            )
        ]
        
        decomposition_results = await asyncio.gather(*decomposition_tasks)
        example_analysis, signature_analysis, pseudocode_analysis = decomposition_results

        # PHASE 2: SYNTHESIZE UNIFIED PROBLEM UNDERSTANDING
        unified_understanding = await self.ensemble(
            instruction="""Synthesize the three analyses into a single coherent problem specification.
            1. Combine example patterns with pseudocode steps.
            2. Integrate signature requirements and type constraints.
            3. Highlight edge cases that must be handled.
            4. Resolve any contradictions between analyses.
            5. Produce a comprehensive implementation checklist.
            Format as: PROBLEM SPECIFICATION followed by IMPLEMENTATION CHECKLIST.""",
            contexts_list=decomposition_results
        )

        # PHASE 3: PARALLEL CANDIDATE GENERATION
        # Generate multiple solution approaches simultaneously
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate Python code based on example pattern extrapolation.
                Use this analysis: {example_analysis}
                
                Requirements:
                - Function name MUST match ENTRY POINT exactly
                - Return types MUST match examples precisely
                - Handle all edge cases identified
                - Code must be minimal and exactly match specification
                - No additional features or validations
                Output ONLY the function code, no explanations.""",
                context=example_analysis
            ),
            self.generate(
                instruction=f"""Generate Python code by implementing the pseudocode steps.
                Use this analysis: {pseudocode_analysis}
                
                Requirements:
                - Translate each pseudocode step literally
                - Preserve function signature exactly
                - Match return types from examples
                - Include edge case handling
                - Keep code simple and direct
                Output ONLY the function code, no explanations.""",
                context=pseudocode_analysis
            ),
            self.generate(
                instruction=f"""Generate Python code by simulating the algorithm step-by-step.
                Use this unified understanding: {unified_understanding}
                
                Approach:
                1. Walk through each example manually
                2. Write code that replicates your manual steps
                3. Generalize from specific examples to universal solution
                4. Ensure function name and return types match exactly
                Output ONLY the function code, no explanations.""",
                context=unified_understanding
            )
        ]
        
        candidate_solutions = await asyncio.gather(*candidate_tasks)

        # PHASE 4: ITERATIVE REFINEMENT
        refined_candidates = []
        for i, candidate in enumerate(candidate_solutions):
            # First revision: Ensure signature and type compliance
            revised = await self.revise(
                instruction=f"""Revise this code to ensure strict compliance:
                1. Function name MUST match ENTRY POINT exactly
                2. Return types MUST match examples (int vs float matters)
                3. Handle all edge cases from analysis: {unified_understanding}
                4. Remove any unnecessary code or features
                5. Keep implementation minimal and exact
                Output ONLY the revised function code.""",
                context=candidate
            )
            
            # Second revision: Validate against examples
            validated = await self.revise(
                instruction=f"""Validate this code against all examples:
                Analysis: {example_analysis}
                Unified understanding: {unified_understanding}
                
                Check:
                1. Does it produce correct output for each example?
                2. Does it handle edge cases correctly?
                3. Is the function name exact?
                4. Are return types precise?
                Fix any issues found. Output ONLY the final function code.""",
                context=revised
            )
            
            refined_candidates.append(validated)

        # PHASE 5: ENSEMBLE SELECTION
        final_code = await self.ensemble(
            instruction="""Select the best solution from candidates:
            1. All candidates must handle all examples correctly
            2. Prefer simplest implementation that meets spec
            3. Ensure function name matches ENTRY POINT exactly
            4. Verify return types match examples precisely
            5. Check edge case handling
            If multiple are equally good, synthesize a hybrid.
            Output ONLY the final function code, no explanations.""",
            contexts_list=refined_candidates
        )

        # PHASE 6: FINAL VALIDATION AND CLEANUP
        final_output = await self.revise(
            instruction="""Final cleanup and validation:
            1. Remove any markdown, explanations, or extra text
            2. Ensure ONLY the function code is present
            3. Verify function name matches ENTRY POINT exactly
            4. Check indentation and Python syntax
            5. Ensure no imports or external dependencies
            Output ONLY the clean function code.""",
            context=final_code
        )

        return final_output