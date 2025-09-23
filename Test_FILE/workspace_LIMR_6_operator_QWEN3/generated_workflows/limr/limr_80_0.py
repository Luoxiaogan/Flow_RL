# Workflow ID: limr_80_0
# Benchmark: limr
# Data Indices: [215, 333]

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

        # STEP 1: Deep Structural Classification
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem:
            1. Identify the primary mathematical domain (algebra, number theory, combinatorics, geometry, probability, etc.)
            2. Detect any hidden constraints, symmetries, or invariants.
            3. Hypothesize 2-3 distinct viable solution strategies with brief rationales.
            4. Flag potential pitfalls: off-by-one errors, ambiguous interpretations, edge cases, or common misconceptions.
            5. Predict the likely form of the solution (e.g., requires modular arithmetic, needs combinatorial counting, involves geometric optimization).
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: Domain-Guided Decomposition
        decomposition = await self.decompose(
            instruction=f"""Based on the classification:
            {classification}

            Decompose this problem into a minimal set of atomic, verifiable subproblems.
            Requirements:
            - Each subproblem must be solvable independently or with specified dependencies.
            - Prioritize subproblems that can be computationally verified.
            - Include at least one subproblem that validates the final answer format (integer 000-999).
            - Order subproblems by dependency (prerequisites first).
            - For each subproblem, specify whether it is primarily symbolic (logic/proof) or computational (calculation).
            Return as a list of dictionaries with 'id', 'description', and 'dependencies'.""",
            context=classification
        )

        # STEP 3: Parallel Strategy Generation (3 independent approaches)
        strategy_instructions = [
            "Solve this problem using algebraic manipulation and equation-solving techniques. Show all steps symbolically before computing final values.",
            "Solve this problem using combinatorial reasoning or counting principles. Model the scenario, account for overcounting, and apply constraints systematically.",
            "Solve this problem using number theory techniques (modular arithmetic, divisibility, prime factorization, etc.). Leverage congruences and integer properties."
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"{instr} The final answer must be an integer between 000 and 999. Show your reasoning step by step.",
                context=""
            ) for instr in strategy_instructions]
        )

        # STEP 4: Dual-Layer Revision (Internal + Cross-Consistency)
        # First revision: Internal consistency check
        internally_revised = await asyncio.gather(
            *[self.revise(
                instruction="""Critique this solution rigorously:
                - Check every mathematical step for validity.
                - Recompute critical values independently.
                - Flag any unjustified assumptions or leaps in logic.
                - If an error is found, correct it and explain the fix.
                - Ensure the final answer is an integer in 000-999 range.
                Preserve the original structure but enhance rigor and precision.""",
                context=attempt
            ) for attempt in strategy_attempts]
        )

        # Second revision: Cross-solution consistency
        cross_revised = []
        for i, solution in enumerate(internally_revised):
            other_solutions = [internally_revised[j] for j in range(len(internally_revised)) if j != i]
            cross_context = "\n\n---\n\n".join([f"ALTERNATIVE SOLUTION {j+1}:\n{sol}" for j, sol in enumerate(other_solutions)])
            
            revised = await self.revise(
                instruction=f"""Compare this solution against the alternative solutions below:
                {cross_context}

                Tasks:
                1. Identify points of agreement and disagreement.
                2. Diagnose the source of any contradictions (e.g., different interpretations, calculation errors, flawed logic).
                3. Resolve contradictions by correcting errors or refining assumptions.
                4. If this solution is irreconcilably flawed, mark it as INVALID.
                5. Otherwise, refine it to align with correct insights from alternatives.
                Output the revised solution or 'INVALID' if unsalvageable.""",
                context=solution
            )
            cross_revised.append(revised)

        # STEP 5: Ensemble Synthesis with Error Diagnosis
        synthesis = await self.ensemble(
            instruction="""You are given multiple candidate solutions (some may be marked INVALID). Your task:
            1. Identify the core correct mathematical insight in each valid solution.
            2. Diagnose and explain errors in invalid or flawed solutions.
            3. Construct a unified, verified solution that combines correct elements and discards flawed ones.
            4. Compute the final integer answer (000-999) with absolute certainty.
            5. Output ONLY the final integer answer, followed by a one-sentence justification.
            Format: "ANSWER: XXX — [justification]".""",
            contexts_list=cross_revised
        )

        # STEP 6: Meta-Validation and Recovery Loop (max 2 iterations)
        final_answer = synthesis
        for recovery_round in range(2):
            # Extract answer for validation
            validation_prompt = await self.generate(
                instruction=f"""Given this proposed solution:
                {final_answer}

                Validate it by:
                1. Extracting the final integer answer (if present).
                2. Substituting it back into the original problem's constraints.
                3. Verifying ALL conditions are satisfied.
                4. If any condition fails, explain why and suggest correction.
                5. If valid, output 'VALIDATED'.
                Be brutally honest — if uncertain, say 'UNCERTAIN'.""",
                context=final_answer
            )

            if "VALIDATED" in validation_prompt or "UNCERTAIN" in validation_prompt:
                break
            else:
                # Trigger recovery: generate meta-critique and restart with refined approach
                meta_critique = await self.generate(
                    instruction=f"""The following solution failed validation:
                    {final_answer}
                    Validation feedback: {validation_prompt}

                    Perform a meta-analysis:
                    1. Why did the initial approaches fail? Misclassification? Missed constraint?
                    2. What mathematical domain or technique was overlooked?
                    3. Propose a radically different solution strategy.
                    4. Suggest specific subproblems to recompute or reinterpret.
                    Output a concise recovery plan.""",
                    context=validation_prompt
                )

                # Generate new solution attempt based on meta-critique
                recovery_attempt = await self.generate(
                    instruction=f"""Based on this recovery plan:
                    {meta_critique}

                    Generate a new solution from scratch. Be meticulous. Verify each step.
                    Final answer must be integer 000-999. Show work clearly.""",
                    context=meta_critique
                )

                # Revise and synthesize with previous attempts
                revised_recovery = await self.revise(
                    instruction="Critique and refine this recovery attempt. Fix any remaining errors. Ensure mathematical rigor.",
                    context=recovery_attempt
                )

                final_answer = await self.ensemble(
                    instruction="""Synthesize the best elements from all previous attempts and this recovery.
                    Output ONLY the final integer answer in format: 'ANSWER: XXX — [one-sentence justification]'.""",
                    contexts_list=cross_revised + [revised_recovery]
                )

        # STEP 7: Final Extraction and Formatting
        answer_extraction = await self.generate(
            instruction="""Extract the final integer answer from this text:
            - Look for patterns like 'ANSWER: XXX' or 'final answer is XXX'.
            - If multiple candidates, choose the one with strongest justification.
            - If none, return '000' as fallback.
            - Output ONLY the three-digit integer (e.g., '123').""",
            context=final_answer
        )

        # Ensure three-digit format
        answer_clean = re.sub(r'\D', '', answer_extraction)
        if len(answer_clean) == 0:
            answer_clean = "000"
        elif len(answer_clean) > 3:
            answer_clean = answer_clean[-3:]
        elif len(answer_clean) < 3:
            answer_clean = answer_clean.zfill(3)

        return answer_clean