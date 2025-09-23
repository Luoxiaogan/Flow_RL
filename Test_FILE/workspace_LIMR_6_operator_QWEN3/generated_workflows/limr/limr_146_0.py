# Workflow ID: limr_146_0
# Benchmark: limr
# Data Indices: [11, 332]

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

        # STEP 1: MATHEMATICAL AUTOPSY — Extract problem structure, entities, constraints, and goal
        problem_analysis = await self.generate(
            instruction="""Perform a deep mathematical autopsy of the problem. Extract:
            1. All given entities (points, numbers, functions, sets, etc.) with their properties.
            2. All constraints (explicit and implicit) — e.g., "obtuse", "on negative x-axis", "largest base", "digit sum not equal to 16".
            3. The unknown(s) to solve for — be specific (e.g., "x-coordinate of third vertex", "maximum value of b").
            4. Mathematical domains involved (geometry, number theory, combinatorics, algebra, etc.).
            5. Potential theorems, formulas, or identities that may apply (e.g., shoelace formula, modular arithmetic, Pythagorean theorem).
            6. Any hidden symmetries, invariants, or transformations that could simplify the problem.
            Format output as a structured markdown list with clear section headers.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY GENERATION — Explore multiple solution archetypes
        strategy_tasks = [
            self.generate(
                instruction=f"""Propose a GEOMETRIC/COORDINATE-BASED solution strategy.
                Given analysis: {problem_analysis}
                Focus on: coordinate systems, vectors, distances, areas, angles, transformations.
                If applicable, suggest specific formulas (e.g., shoelace, dot product, distance formula).
                Outline step-by-step how to translate the problem into geometric computations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a NUMBER THEORY/ALGEBRAIC solution strategy.
                Given analysis: {problem_analysis}
                Focus on: modular arithmetic, divisibility, polynomial expansions, base representations, Diophantine equations.
                If applicable, suggest algebraic manipulations or substitutions.
                Outline step-by-step how to reduce the problem to solvable equations or congruences.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a COMBINATORIAL/PROBABILISTIC solution strategy.
                Given analysis: {problem_analysis}
                Focus on: counting principles, permutations, combinations, probability distributions, recursive relations.
                If applicable, suggest combinatorial identities or generating functions.
                Outline step-by-step how to model the problem combinatorially.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose an OPTIMIZATION/INEQUALITY-BASED solution strategy.
                Given analysis: {problem_analysis}
                Focus on: maxima/minima, inequalities (AM-GM, Cauchy-Schwarz), calculus (if applicable), boundary analysis.
                Outline step-by-step how to frame the problem as an optimization task.""",
                context=""
            )
        ]

        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # STEP 3: ENSEMBLE — Synthesize or select the most promising strategy
        selected_strategy = await self.ensemble(
            instruction="""Evaluate the four proposed strategies:
            1. Which is most directly applicable given the problem constraints and unknowns?
            2. Which has the clearest computational pathway?
            3. Which minimizes risk of logical gaps or constraint violations?
            4. If multiple are viable, synthesize a hybrid approach.
            Output the chosen strategy with a clear justification and a refined step-by-step plan.""",
            contexts_list=strategy_candidates
        )

        # STEP 4: DECOMPOSE — Break into dependency-aware subproblems
        subproblems = await self.decompose(
            instruction=f"""Decompose the selected strategy into atomic, ordered subproblems:
            - Each subproblem must be self-contained and solvable with clear inputs/outputs.
            - Specify dependencies (e.g., "Subproblem 2 requires output of Subproblem 1").
            - Include validation steps (e.g., "Verify obtuseness after finding coordinates").
            - For computational steps, specify exact formulas or algorithms to use.
            Strategy: {selected_strategy}""",
            context=selected_strategy
        )

        # STEP 5: EXECUTE SUBPROBLEMS SEQUENTIALLY WITH VALIDATION
        solution_context = ""
        for i, sp in enumerate(subproblems):
            sp_id = sp['id']
            sp_desc = sp['description']
            deps = sp.get('dependencies', "").split(",") if sp.get('dependencies') else []

            # Wait for dependencies (in real implementation, you'd track completed subproblem outputs)
            # For simplicity, we assume sequential execution respecting dependency order
            
            # Generate solution for this subproblem
            sub_solution = await self.generate(
                instruction=f"""Solve subproblem {sp_id}: {sp_desc}
                Use the following context from previous steps: {solution_context}
                Be precise, show key steps, and if computational, specify exact expressions.
                If this is a validation step, explicitly state pass/fail criteria.""",
                context=solution_context
            )

            # If this is a computational step, execute with Programmer
            if any(kw in sp_desc.lower() for kw in ["compute", "calculate", "solve for", "find value", "determine"]):
                code_result = await self.programmer(
                    instruction=f"""Generate and execute Python code to solve: {sp_desc}
                    Use the following context: {sub_solution}
                    Ensure code is mathematically precise, handles edge cases, and outputs exact values.
                    If multiple solutions, filter by problem constraints (e.g., x<0, largest b, etc.).""",
                    context=sub_solution
                )
                sub_solution = f"{sub_solution}\n\nPROGRAMMER OUTPUT:\n{code_result}"

            # Validate if this step has validation requirement
            if "verify" in sp_desc.lower() or "check" in sp_desc.lower():
                validation = await self.generate(
                    instruction=f"""Validate the following solution against problem constraints:
                    Subproblem: {sp_desc}
                    Proposed Solution: {sub_solution}
                    Original Problem Constraints: {problem_analysis}
                    Output 'VALID' if all constraints satisfied, else explain failure.""",
                    context=sub_solution
                )
                if "VALID" not in validation:
                    # Revise strategy or subproblem approach
                    sub_solution = await self.revise(
                        instruction=f"""Revise the solution to satisfy constraints:
                        Validation Feedback: {validation}
                        Original Subproblem: {sp_desc}
                        Previous Attempt: {sub_solution}""",
                        context=sub_solution
                    )

            solution_context += f"\n\n--- Subproblem {sp_id} ---\n{sub_solution}"

        # STEP 6: FINAL SYNTHESIS AND ANSWER EXTRACTION
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer from the solution context.
            - Must be an integer between 000 and 999.
            - If multiple candidates, select the one satisfying ALL problem constraints.
            - Format as: \\boxed{XXX} where XXX is the 3-digit answer (pad with leading zeros if needed).
            - Include a one-sentence justification referencing key steps.""",
            context=solution_context
        )

        # Ensure answer is in correct format
        match = re.search(r'\\boxed\{(\d{1,3})\}', final_answer)
        if match:
            num = int(match.group(1))
            formatted_answer = f"\\boxed{{{num:03d}}}"
            return formatted_answer
        else:
            # Fallback: return raw summary if extraction fails
            return final_answer