# Workflow ID: limr_56_0
# Benchmark: limr
# Data Indices: [56, 87]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: Problem Classification and Strategy Selection
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your task:

1. Classify the problem type with high specificity (e.g., not just 'algebra' but 'piecewise function root finding with domain constraints').
2. Identify all mathematical domains involved (algebra, number theory, combinatorics, geometry, etc.).
3. Extract key components: variables, functions, constraints, target outputs.
4. Determine if the solution requires exact symbolic manipulation, numerical computation, combinatorial counting, or geometric reasoning.
5. List potential solution strategies ranked by apparent suitability.
6. Flag any potential pitfalls or subtle constraints (e.g., domain restrictions, integer-only solutions, hidden symmetries).

Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Exploration
        # Dynamically construct instructions based on problem type
        symbolic_approach = await self.generate(
            instruction=f"""Based on this problem analysis:
{problem_analysis}

Develop a complete symbolic/mathematical solution. Steps:
- Break down the problem into logical steps.
- Apply appropriate theorems, identities, or algebraic manipulations.
- Show all work with clear justifications.
- Handle edge cases and domain restrictions explicitly.
- Arrive at a final answer (integer 000-999) with boxed notation.

If the problem involves functions, solve equation(s) systematically. If combinatorics, justify counting principles. If number theory, show modular arithmetic or divisibility arguments.""",
            context=""
        )

        computational_approach = await self.programmer(
            instruction=f"""Based on this problem analysis:
{problem_analysis}

Generate Python code to solve the problem computationally. Requirements:
- Use exact arithmetic (no floating point unless unavoidable).
- Handle all cases and constraints identified in the analysis.
- If symbolic solution is needed, use sympy.
- If counting, use combinatorial libraries or explicit loops with careful bounds.
- Output must be a single integer between 000 and 999.
- Include verification steps within the code where possible.

Return the code and its output.""",
            context="",
            max_retries=3
        )

        conceptual_approach = await self.generate(
            instruction=f"""Based on this problem analysis:
{problem_analysis}

Reframe the problem from a different mathematical perspective. For example:
- If algebraic, consider geometric interpretation.
- If combinatorial, consider generating functions or recursive relations.
- If functional, consider fixed points or transformation of variables.
- If number-theoretic, consider prime factorization or modular patterns.

Develop a solution using this alternative lens. Show how this perspective simplifies or provides insight. Derive the answer independently.""",
            context=""
        )

        # Ensemble the parallel approaches
        candidate_solutions = [symbolic_approach, computational_approach, conceptual_approach]
        synthesized_solution = await self.ensemble(
            instruction="""You are given three candidate solutions to the same mathematical problem. Your task:

1. Compare the solutions for consistency in final answer.
2. If all agree, select the most clearly justified solution.
3. If they disagree, identify which solution(s) have flaws and select the most robust.
4. Synthesize a final answer by combining the strongest elements of each approach.
5. Output ONLY the final integer answer (000-999) in boxed format: \\boxed{{answer}}.

Do not include explanations or working — only the boxed integer.""",
            contexts_list=candidate_solutions
        )

        # PHASE 3: Adversarial Verification Loop
        refined_solution = synthesized_solution
        for iteration in range(2):  # Allow up to 2 refinement cycles
            critique = await self.revise(
                instruction=f"""Adversarial critique of this solution:
{refined_solution}

Assume this solution is INCORRECT. Your task:
- Find the flaw, no matter how small.
- Check: domain violations, arithmetic errors, missed cases, logical gaps.
- If it involves functions, verify all cases. If exponents, check simplification rules.
- If no flaw found, state "VERIFIED: No flaws detected."

If flaws are found, explain them concisely.""",
                context=refined_solution
            )

            if "flaw" not in critique.lower() and "error" not in critique.lower() and "invalid" not in critique.lower():
                break  # No flaws found, exit loop
            else:
                # Revise based on critique
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution to fix the following critique:
{critique}

Incorporate the correction while preserving the correct parts. Output the complete corrected solution with final answer in \\boxed{{}}.""",
                    context=refined_solution
                )

        # Final computational verification
        answer_summary = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution below. 
It must be an integer between 000 and 999. Ignore all text, justifications, and working.
If multiple answers, list them all. Format: comma-separated integers.""",
            context=refined_solution
        )

        # Use programmer to validate the answer by plugging back in (if applicable)
        validation_result = await self.programmer(
            instruction=f"""Validate the answer(s) {answer_summary} by computational verification.

Steps:
1. Parse the original problem and the proposed answer(s).
2. Write code to plug the answer(s) back into the original problem conditions.
3. Verify that each answer satisfies ALL problem constraints and equations.
4. Output 'VALID' if all answers check out, 'INVALID' if any fail, with explanation.

Example: If problem is f(x)=-5, compute f(answer) and check if equals -5.""",
            context="",
            max_retries=2
        )

        # If validation fails, attempt one final revision
        if "invalid" in validation_result.lower():
            final_revision = await self.revise(
                instruction=f"""The solution failed computational validation:
{validation_result}

Re-solve the problem from scratch with extreme attention to the validation failure. 
Output only the corrected final answer in \\boxed{{}} format.""",
                context=problem_analysis
            )
            return final_revision

        return refined_solution