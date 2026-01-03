# Workflow ID: mgsmbn_125_0
# Benchmark: mgsmbn
# Data Indices: [91, 8]

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

        # STEP 1: Hierarchical Decomposition
        decomposition = await self.decompose(
            instruction="""Break this Bengali math problem into atomic, ordered subproblems. For each:
            1. Identify all numerical entities and their semantic roles (cost, revenue, rate, time, quantity).
            2. Extract temporal/causal dependencies (e.g., 'after', 'because', 'then').
            3. Define the target variable and its expected unit.
            4. List implicit constraints (e.g., non-negative profit, whole years).
            Structure each subproblem as: [ID]: [Description] (depends on: [IDs])""",
            context=""
        )

        # STEP 2: Parallel Solution Generation (3 Lenses)
        algebraic_task = self.generate(
            instruction="""Translate the problem into algebraic equations. Define variables explicitly. 
            Show step-by-step derivation. Track units at each step. Highlight any assumptions made.
            Format: Equations → Substitutions → Solution → Unit Verification.""",
            context=""
        )
        
        tabular_task = self.generate(
            instruction="""Model the problem as a chronological table of state changes. 
            For each time step or event: 
            - Initial state
            - Action/Change
            - Resulting state
            - Cumulative effect
            End with final answer and unit consistency check.""",
            context=""
        )
        
        unit_tracking_task = self.generate(
            instruction="""Solve using dimensional analysis. Write each quantity with explicit units. 
            Show unit cancellation step-by-step. Verify final answer has correct dimension. 
            If units don't cancel as expected, flag the inconsistency.""",
            context=""
        )

        # Execute parallel tasks
        algebraic_sol, tabular_sol, unit_sol = await asyncio.gather(
            algebraic_task, tabular_task, unit_tracking_task
        )

        # STEP 3: Independent Validation of Each Path
        validation_tasks = []
        for sol, lens in [(algebraic_sol, "algebraic"), (tabular_sol, "tabular"), (unit_sol, "unit-tracking")]:
            validation_tasks.append(
                self.revise(
                    instruction=f"""Critique this {lens} solution:
                    1. Check arithmetic accuracy.
                    2. Verify unit consistency.
                    3. Confirm alignment with problem constraints.
                    4. Identify any missing steps or logical gaps.
                    If flawless, respond 'VALID: [summary]'. If flawed, respond 'INVALID: [specific issues]'.""",
                    context=sol
                )
            )
        
        validations = await asyncio.gather(*validation_tasks)

        # STEP 4: Ensemble Synthesis with Discrepancy Handling
        synthesis = await self.ensemble(
            instruction="""Synthesize the three solutions and their validations:
            - If all are VALID and agree numerically, select any.
            - If two agree and one differs, select the majority.
            - If all differ, identify the most logically complete solution.
            - If any solution is INVALID, exclude it unless others are also flawed.
            Output the chosen solution with a confidence flag (HIGH/MEDIUM/LOW) and a 1-sentence rationale.""",
            contexts_list=[f"Solution: {s}\nValidation: {v}" for s, v in zip([algebraic_sol, tabular_sol, unit_sol], validations)]
        )

        # STEP 5: Refinement Loop (if LOW confidence or discrepancies)
        confidence = "HIGH" if "HIGH" in synthesis else "LOW"
        final_model = synthesis
        
        if confidence == "LOW":
            for _ in range(2):  # Max 2 refinement iterations
                refinement = await self.revise(
                    instruction="""The solution has LOW confidence. Re-examine the original problem and validations.
                    Identify the root cause of discrepancy: 
                    - Misinterpreted entities? 
                    - Incorrect operation sequencing?
                    - Unit conversion error?
                    Regenerate the most plausible solution with explicit error correction.""",
                    context=final_model
                )
                
                # Quick validation
                recheck = await self.revise(
                    instruction="Final verification: Does this solution satisfy all constraints and units? YES/NO + reason.",
                    context=refinement
                )
                
                if "YES" in recheck:
                    final_model = refinement
                    break
                else:
                    final_model = refinement  # Proceed with best effort

        # STEP 6: Code Generation with Embedded Sanity Checks
        code_result = await self.programmer(
            instruction=f"""Implement the validated mathematical model from: {final_model}
            Requirements:
            - Define all variables with comments explaining their real-world meaning.
            - Include unit assertions (e.g., assert profit >= 0, "Profit cannot be negative").
            - Print intermediate values for auditability.
            - Final answer must be a single float or int, printed as: "ANSWER: <value>".
            - Handle edge cases (e.g., fractional years → ceiling).""",
            context=final_model,
            max_retries=3
        )

        # STEP 7: Extract Final Numerical Answer
        # Look for "ANSWER: <number>" pattern
        match = re.search(r"ANSWER:\s*([\-+]?\d*\.?\d+)", code_result)
        if match:
            return float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
        else:
            # Fallback: Extract last number from code output
            numbers = re.findall(r"([\-+]?\d*\.?\d+)", code_result)
            if numbers:
                last_num = numbers[-1]
                return float(last_num) if '.' in last_num else int(last_num)
            else:
                raise ValueError("No numerical answer found in final output")