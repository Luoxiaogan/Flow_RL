# Workflow ID: mbppplus_40_0
# Benchmark: mbppplus
# Data Indices: [190, 37, 16]

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

        # Step 1: Deep problem characterization
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive structural analysis of this programming problem. Address:

1. Problem Genre Classification:
   - Is this primarily a mathematical, structural (data transformation), logical, or algorithmic problem?
   - Justify your classification with evidence from the problem statement.

2. Input/Output Specification:
   - What are the expected input types and structures?
   - What is the required return type and format?
   - Are there any implicit type constraints (e.g., must return tuple, not list)?

3. Edge Case Identification:
   - What are the critical edge cases? (e.g., empty inputs, single elements, zeros, negatives, nested structures)
   - What boundary conditions must be handled?

4. Solution Strategy Options:
   - Propose 2-3 distinct high-level approaches to solve this.
   - For each, outline the core logic and potential pitfalls.

5. Validation Requirements:
   - What must a correct solution absolutely satisfy?
   - What would constitute a silent failure (e.g., wrong return type)?

Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Parallel solution generation - three strategic branches
        math_approach, algo_approach, struct_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using a mathematical/formulaic approach.
Context: {problem_analysis}

Guidelines:
- If the problem involves formulas, physics, or arithmetic sequences, derive the exact mathematical expression.
- Handle floating-point precision and rounding as needed.
- Include necessary imports (math, etc.) inside the function if required.
- Return EXACTLY the required type (int, float, tuple, etc.) - verify against problem's return specification.
- Test edge cases: zero inputs, negative values, extreme magnitudes.
- Output ONLY the function implementation with correct signature - no explanations.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using an iterative/algorithmic approach.
Context: {problem_analysis}

Guidelines:
- Use loops, conditionals, and state variables if the problem involves steps, jumps, or progressive computation.
- Handle termination conditions and edge cases explicitly (empty inputs, single elements).
- Optimize for clarity over cleverness - readable code is debuggable code.
- Ensure type consistency: if input is tuple, output should respect immutability unless specified otherwise.
- Output ONLY the function implementation with correct signature - no explanations.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using a structural/data-transformation approach.
Context: {problem_analysis}

Guidelines:
- If the problem involves nested structures, filtering, or type-based operations, use structural decomposition.
- Handle recursion or iteration over complex data types (tuples, lists, sets) with care for immutability and order.
- Remove or transform elements based on type or value conditions.
- Preserve required structure (e.g., return tuple if input was tuple).
- Output ONLY the function implementation with correct signature - no explanations.""",
                context=problem_analysis
            )
        )

        # Step 3: Parallel validation of each candidate
        validated_candidates = await asyncio.gather(
            self.revise(
                instruction="""Critically validate this solution against the problem's requirements and edge cases.
- Simulate execution with edge inputs: empty, single-element, zero, negative, nested, maximum values.
- Does it crash? Return wrong type? Violate immutability? Fail silently?
- Check import statements: are they inside the function? Correct modules?
- Verify function signature matches exactly (parameter names, order).
- If flawed, rewrite to fix ALL issues while preserving core logic.
- Output ONLY the corrected function - no commentary.""",
                context=math_approach
            ),
            self.revise(
                instruction="""Critically validate this solution against the problem's requirements and edge cases.
- Simulate execution with edge inputs: empty, single-element, zero, negative, nested, maximum values.
- Does it crash? Return wrong type? Violate immutability? Fail silently?
- Check import statements: are they inside the function? Correct modules?
- Verify function signature matches exactly (parameter names, order).
- If flawed, rewrite to fix ALL issues while preserving core logic.
- Output ONLY the corrected function - no commentary.""",
                context=algo_approach
            ),
            self.revise(
                instruction="""Critically validate this solution against the problem's requirements and edge cases.
- Simulate execution with edge inputs: empty, single-element, zero, negative, nested, maximum values.
- Does it crash? Return wrong type? Violate immutability? Fail silently?
- Check import statements: are they inside the function? Correct modules?
- Verify function signature matches exactly (parameter names, order).
- If flawed, rewrite to fix ALL issues while preserving core logic.
- Output ONLY the corrected function - no commentary.""",
                context=struct_approach
            )
        )

        # Step 4: Ensemble synthesis - merge best elements
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these candidates:

1. Compare for:
   - Correctness on edge cases (empty, zero, negatives, nested, boundaries)
   - Adherence to return type and function signature
   - Code clarity and maintainability
   - Efficiency (avoid unnecessary loops or computations)
   - Robustness (handles unexpected but valid inputs)

2. If one candidate is clearly superior, select it.
3. If multiple are valid, merge their strengths:
   - Take the clearest logic from one, the edge-case handling from another.
   - Resolve contradictions by favoring type safety and specification compliance.

4. Final output MUST be:
   - ONLY the function implementation
   - With correct signature and parameter names
   - With necessary imports inside the function
   - No extra text, markdown, or explanations

Your goal: produce the most robust, correct, and specification-compliant solution possible.""",
            contexts_list=validated_candidates
        )

        # Step 5: Final hardening - enforce purity and signature compliance
        hardened_solution = await self.revise(
            instruction="""Final hardening pass:

1. Strip ALL non-code text: no comments, no markdown, no explanations.
2. Verify function signature matches EXACTLY (name, parameter names, order).
3. Ensure imports are inside the function if needed.
4. Confirm return type matches problem specification (tuple vs list vs int).
5. Remove any debugging prints or extra statements.
6. Output ONLY the raw Python function - nothing else.

This is the final deliverable - it must be production-ready and pass all hidden test cases.""",
            context=synthesized_solution
        )

        # Optional: One-shot refinement loop if synthesis failed (basic validation)
        if "def " not in hardened_solution or "return" not in hardened_solution:
            # Fallback: regenerate with stricter constraints
            hardened_solution = await self.generate(
                instruction=f"""REGENERATE with absolute strictness:
Problem context: {problem_analysis}

- Output ONLY a valid Python function.
- Must include 'def function_name(...):' and 'return ...'
- No explanations. No markdown. No comments.
- Match signature exactly.
- Handle edge cases: empty, zero, negatives, type boundaries.

Final code only:""",
                context=""
            )

        return hardened_solution