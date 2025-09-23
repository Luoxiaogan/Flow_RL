# Workflow ID: mbppplus_22_0
# Benchmark: mbppplus
# Data Indices: [79, 248, 49]

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

        # Phase 1: Parallel Problem Decomposition
        decomposition_tasks = [
            self.generate(
                instruction="""Analyze the mathematical or logical essence of this programming problem.
                - What is the core operation or transformation being requested?
                - Is this a search, comparison, aggregation, validation, or generation task?
                - What invariants or properties must hold for a correct solution?
                - Express the problem in abstract mathematical or logical terms.
                - Identify any known algorithms or patterns that apply (e.g., sorting, sieving, traversal).
                Provide a concise but rigorous conceptual breakdown.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all data types, structures, and interface requirements.
                - What are the input parameter types and expected return type?
                - Are there constraints on mutability, order preservation, or uniqueness?
                - Must the solution handle specific edge cases (empty, single element, duplicates)?
                - Extract the exact function signature and naming requirements.
                - Note any implicit type conversions or boundary conditions.
                Format as a structured type specification with examples.""",
                context=""
            ),
            self.generate(
                instruction="""Enumerate potential edge cases, failure modes, and stress tests.
                - What inputs would break a naive implementation?
                - Consider: empty inputs, single elements, duplicates, negative numbers, zeros, max values.
                - What are the performance boundaries? (e.g., large inputs, recursion limits)
                - Are there type coercion pitfalls or floating-point precision issues?
                - List at least 5 specific edge case scenarios with expected behaviors.
                Think like an adversarial tester trying to break the solution.""",
                context=""
            )
        ]
        
        math_analysis, type_analysis, edge_analysis = await asyncio.gather(*decomposition_tasks)

        # Phase 2: Parallel Solution Strategy Generation
        strategy_context = f"""Mathematical Analysis: {math_analysis}
Type & Interface Analysis: {type_analysis}
Edge Case Analysis: {edge_analysis}"""

        strategy_tasks = [
            self.generate(
                instruction=f"""Generate Solution Sketch A: Direct/Imperative Approach
Context: {strategy_context}

Implement a straightforward, step-by-step solution:
- Use explicit loops and conditionals where appropriate.
- Prioritize clarity and direct translation of problem logic.
- Handle all edge cases identified above.
- Ensure exact function signature and return type compliance.
- Include necessary imports inside the function if needed.
- Return ONLY the function implementation, no explanations.""",
                context=strategy_context
            ),
            self.generate(
                instruction=f"""Generate Solution Sketch B: Functional/Set-Theoretic Approach
Context: {strategy_context}

Implement using functional programming or set operations:
- Leverage built-in functions (map, filter, reduce, set operations, comprehensions).
- Consider mathematical properties (e.g., sorting for comparison, sieves for primes).
- Handle edge cases through preconditions or guards.
- Maintain exact signature and return type.
- Include necessary imports.
- Return ONLY the function implementation.""",
                context=strategy_context
            ),
            self.generate(
                instruction=f"""Generate Solution Sketch C: Optimized/Mathematical Approach
Context: {strategy_context}

Implement using mathematical insights or optimized algorithms:
- Apply number theory, combinatorics, or algorithmic optimizations.
- Precompute values or use dynamic programming if beneficial.
- Ensure correctness across all edge cases.
- Match exact function signature and return type.
- Include necessary imports.
- Return ONLY the function implementation.""",
                context=strategy_context
            )
        ]
        
        sketch_a, sketch_b, sketch_c = await asyncio.gather(*strategy_tasks)

        # Phase 3: Ensemble Synthesis and Validation
        sketches = [sketch_a, sketch_b, sketch_c]
        
        synthesized_draft = await self.ensemble(
            instruction=f"""Synthesize the best elements from all solution sketches into one robust implementation.
Context: {strategy_context}

Criteria:
1. Correctness: Must handle all edge cases from edge_analysis.
2. Precision: Must match exact function signature and return type from type_analysis.
3. Robustness: No assumptions about input beyond what's specified.
4. Clean Code: Readable, efficient, minimal dependencies.
5. Format: Return ONLY the function implementation with imports, no markdown or explanations.

Select and merge the strongest approach, incorporating fixes or improvements from others.""",
            contexts_list=sketches
        )

        # Validation and Iterative Refinement Loop
        current_code = synthesized_draft
        for iteration in range(3):  # Max 3 refinement cycles
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this code against all known requirements and edge cases.
Code to Validate:
{current_code}

Context: {strategy_context}

Checklist:
- Does it handle ALL edge cases listed in edge_analysis?
- Does it match the EXACT function signature and return type?
- Are there any logical errors, off-by-one mistakes, or type mismatches?
- Is it defensively coded against invalid inputs (if required)?
- Are imports correct and minimal?
- Is the output format exactly as required (no extra text, pure Python)?

If any issues are found, describe them SPECIFICALLY with line numbers or logic errors.
If no issues, respond with 'VALIDATED: No issues found.'""",
                context=current_code
            )

            if "VALIDATED: No issues found." in validation_feedback:
                break

            # Revise based on specific feedback
            current_code = await self.revise(
                instruction=f"""Revise the code to fix ALL issues identified in the validation feedback.
Validation Feedback: {validation_feedback}

Requirements:
- Preserve the core logic unless it's fundamentally flawed.
- Fix edge case handling, type mismatches, or signature errors.
- Maintain exact output format: ONLY the function implementation.
- Do not introduce new bugs or assumptions.
- Include necessary imports inside the function if needed.

Return the complete revised function implementation.""",
                context=current_code
            )
        else:
            # If we exhausted iterations, use the last revision
            pass

        # Final Sanitization: Ensure exact format compliance
        final_code = await self.generate(
            instruction=f"""Ensure this code matches the EXACT required output format.
Code: {current_code}

Rules:
- Must be pure Python code with correct function signature.
- Must include any necessary imports at the top of the function body.
- Must return ONLY the function implementation - no explanations, no markdown.
- Function name and parameters must match the problem specification exactly.
- Return type must be precisely as required (list, tuple, int, bool, etc.).

If any formatting issues exist, correct them. Otherwise, return the code unchanged.""",
            context=current_code
        )

        return final_code