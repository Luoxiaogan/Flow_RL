# Workflow ID: humaneval_34_0
# Benchmark: humaneval
# Data Indices: [67, 23]

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
        Universal code generation workflow that adapts to problem complexity.
        Uses classification, parallel analysis, synthesis, and iterative refinement.
        """
        import asyncio
        import re

        # STEP 1: CLASSIFY PROBLEM & EXTRACT KEY COMPONENTS
        classification = await self.generate(
            instruction="""Thoroughly analyze this code generation problem:

1. Extract function name, parameters, and return type from signature.
2. Parse docstring examples: count them, identify input patterns, output patterns, and edge cases.
3. Classify problem type: 
   - 'trivial' (direct builtin mapping, e.g., len, str, int)
   - 'pattern_extraction' (requires parsing strings, regex, or structured extraction)
   - 'mathematical' (involves formulas, arithmetic, or logic)
   - 'algorithmic' (requires loops, recursion, or state)
4. Estimate complexity: low (1-2 steps), medium (3-5 steps), high (5+ steps or edge cases)
5. List potential edge cases not shown in examples (empty inputs, zeros, negatives, type mismatches)
6. Identify critical constraints: exact function name, return type precision, no over-engineering

Output structured analysis in this format:
CLASSIFICATION: [type]
COMPLEXITY: [low|medium|high]
EDGE_CASES: [comma separated list]
CONSTRAINTS: [comma separated list]
FUNCTION_NAME: [exact name]
RETURN_TYPE: [inferred from examples]""",
            context=""
        )

        # STEP 2: CONDITIONAL BRANCHING BASED ON CLASSIFICATION
        if "trivial" in classification.lower() and "low" in classification.lower():
            # Fast path for trivial problems
            solution = await self.generate(
                instruction=f"""Generate minimal, correct Python function based on specification.
Classification: {classification}

Rules:
- Use built-in functions if directly applicable (e.g., len for string length)
- Match function name EXACTLY
- Return type must match examples precisely
- No extra logic, imports, or comments
- Handle edge cases mentioned in classification

Generate ONLY the function code, nothing else.""",
                context=""
            )
            # Single revision for safety
            final_solution = await self.revise(
                instruction="""Critique this code:
1. Does function name match ENTRY POINT exactly?
2. Does it handle all example cases from docstring?
3. Are return types correct (int vs float)?
4. Are edge cases from classification handled?
5. Is there any over-engineering?

If any issue found, fix it. Otherwise, return unchanged.""",
                context=solution
            )
            return final_solution

        else:
            # Rich path for complex problems
            # STEP 3: PARALLEL ANALYSIS (Diamond Pattern Fork)
            analysis_tasks = [
                self.generate(
                    instruction=f"""ANALYSIS PERSPECTIVE 1: INPUT PARSING
Classification: {classification}

Focus exclusively on input processing:
- What format are inputs? (string, number, list, etc.)
- How to extract necessary values? (split, regex, json, etc.)
- What preprocessing is needed?
- What edge cases in input format? (empty, malformed, extreme values)

Provide detailed parsing strategy with code snippets if helpful.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""ANALYSIS PERSPECTIVE 2: OUTPUT DERIVATION
Classification: {classification}

Focus exclusively on output calculation:
- What transformation or formula connects inputs to outputs?
- What mathematical operations or logical conditions?
- How to handle edge cases in calculation?
- What intermediate variables or steps needed?

Provide step-by-step derivation with examples from docstring.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""ANALYSIS PERSPECTIVE 3: EDGE CASES & ROBUSTNESS
Classification: {classification}

Focus exclusively on edge cases and robustness:
- List all edge cases from classification plus 3 new ones
- How should each edge case be handled?
- What validation or error handling needed?
- What assumptions must NOT be made?

Provide comprehensive edge case handling strategy.""",
                    context=""
                )
            ]
            
            # Execute parallel analyses
            analyses = await asyncio.gather(*analysis_tasks)
            
            # STEP 4: SYNTHESIZE ANALYSES INTO SOLUTION (Diamond Pattern Merge)
            synthesized_solution = await self.ensemble(
                instruction=f"""SYNTHESIZE FINAL SOLUTION
Classification: {classification}

You have three analysis perspectives:
1. Input Parsing
2. Output Derivation  
3. Edge Cases & Robustness

Synthesize them into one complete, correct Python function:
- Use simplest approach that satisfies all requirements
- Match function name EXACTLY
- Handle all edge cases mentioned in any analysis
- Return type must match examples precisely
- No over-engineering - implement exactly what's specified
- Include necessary imports if any (but prefer built-ins)

Generate ONLY the function code, nothing else.""",
                contexts_list=analyses
            )
            
            # STEP 5: ITERATIVE REFINEMENT (Max 2 iterations)
            current_solution = synthesized_solution
            for iteration in range(2):
                revision = await self.revise(
                    instruction=f"""CRITICAL REVISION #{iteration + 1}
Classification: {classification}

Critique this code against these criteria:
1. Function name matches ENTRY POINT exactly? (CRITICAL)
2. All example cases from docstring work? (Test mentally)
3. Return types correct? (int vs float matters)
4. All edge cases from classification and analyses handled?
5. No unnecessary complexity or imports?
6. Code is clean, readable, and efficient?

If ANY issue found, fix it precisely. If perfect, return unchanged.
DO NOT add comments or docstrings - only functional code.""",
                    context=current_solution
                )
                
                # Check if revision made significant changes (simple heuristic)
                if revision.strip() == current_solution.strip():
                    break  # No changes, exit loop
                current_solution = revision
            
            return current_solution