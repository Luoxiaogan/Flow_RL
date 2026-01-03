# Workflow ID: limr_43_0
# Benchmark: limr
# Data Indices: [3, 15]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import json

        # STEP 1: PARALLEL PROBLEM FINGERPRINTING & STRATEGY HYPOTHESIS GENERATION
        classification, decomposition_hypotheses = await asyncio.gather(
            self.generate(
                instruction="""Perform deep semantic classification of this mathematical problem. Analyze:
                1. Primary domain (algebra, geometry, number theory, combinatorics, etc.) and secondary domains involved.
                2. Key mathematical objects (complex numbers, polynomials, sequences, geometric figures, etc.).
                3. Dominant operations (modular arithmetic, trigonometric identities, recursive relations, coordinate transformations, etc.).
                4. Likely proof techniques (induction, contradiction, generating functions, symmetry exploitation, etc.).
                5. Computational tractability: Can brute-force or numerical methods assist? Or is pure symbolic derivation required?
                6. Answer format expectations: Is the answer likely an integer? A fraction? A radical expression?
                7. Known problem archetypes this resembles (e.g., "roots of unity filter", "Vieta jumping", "geometric probability").
                Output a structured JSON with keys: domain, objects, operations, techniques, computability, format, archetypes.""",
                context=""
            ),
            self.decompose(
                instruction="""Generate 3 distinct decomposition strategies for this problem, each based on a different mathematical perspective:
                Strategy A: Algebraic/symbolic manipulation focus.
                Strategy B: Geometric/visual or coordinate-based interpretation.
                Strategy C: Combinatorial or number-theoretic reduction.
                For each strategy, break the problem into 3-5 subproblems with clear dependencies. Prioritize decompositions that isolate computational steps from conceptual leaps.
                Format each subproblem with: id, description, dependencies (comma-separated), and estimated difficulty (low/medium/high).""",
                context=""
            )
        )

        # STEP 2: VALIDATE & REFINE CLASSIFICATION
        validated_classification = await self.revise(
            instruction="""Critically validate the classification. Check for:
            - Overlooked mathematical objects or hidden symmetries.
            - Mismatch between suggested techniques and problem constraints.
            - Under/over-estimation of computational feasibility.
            - Consistency with known problem archetypes.
            If confidence is below 90%, propose an alternative classification hypothesis. Output revised JSON with 'confidence_score' (0-100) and 'alternative_hypotheses' (list).""",
            context=classification
        )

        # STEP 3: PARALLEL STRATEGY EXPLORATION (DIAMOND PATTERN)
        strategy_attempts = []
        for i, strategy in enumerate(decomposition_hypotheses[:3]):  # Limit to top 3 for efficiency
            try:
                # Convert decomposition to executable plan
                subproblem_context = json.dumps(strategy, indent=2)
                
                # Generate solution attempt for this decomposition
                attempt = await self.generate(
                    instruction=f"""Execute this decomposition strategy:
                    {subproblem_context}
                    
                    For each subproblem in dependency order:
                    1. State the subproblem clearly.
                    2. Show all mathematical reasoning — no skipped steps.
                    3. Verify intermediate results (e.g., plug back into original equation, check boundary cases).
                    4. Flag any assumptions made.
                    5. If stuck, propose an alternative approach for that subproblem.
                    Output must be structured: ## Subproblem [id] → Solution → Verification → Status (SOLVED/PARTIAL/STUCK).""",
                    context=subproblem_context
                )
                
                # Validate and refine the attempt
                refined_attempt = await self.revise(
                    instruction="""Rigorously verify this solution attempt:
                    - Check algebraic manipulations for sign errors, division by zero, or invalid assumptions.
                    - Confirm that all dependencies are satisfied before proceeding.
                    - Validate final answer against problem constraints (e.g., positivity, integer requirement).
                    - If errors found, correct them and re-verify. If unfixable, mark as INVALID.
                    Output: Verified solution with error log (if any) and confidence flag (HIGH/MEDIUM/LOW).""",
                    context=attempt
                )
                
                strategy_attempts.append(refined_attempt)
                
            except Exception as e:
                # Fallback: generate a direct solution attempt
                fallback = await self.generate(
                    instruction=f"""Direct solution attempt (fallback for failed decomposition):
                    Problem classification: {validated_classification}
                    Ignore decomposition — solve holistically with emphasis on symbolic manipulation and known identities.
                    Show all steps. Verify twice. Box final answer.""",
                    context=""
                )
                strategy_attempts.append(fallback)

        # STEP 4: SYNTHESIZE & RESOLVE CONFLICTS
        synthesized = await self.ensemble(
            instruction="""Synthesize all solution attempts into a single authoritative answer:
            1. If all attempts agree, output the consensus answer.
            2. If attempts conflict, prioritize by: 
               - Analytic derivation over numerical approximation.
               - Higher confidence scores.
               - Fewer assumptions.
            3. If conflicts remain, merge compatible partial results and flag contradictions for review.
            4. Final output must be an integer between 000 and 999. If answer is fractional or symbolic, compute exact integer value.
            5. Include brief justification for chosen answer and rejected alternatives.
            FORMAT: 
            FINAL_ANSWER: [integer]
            JUSTIFICATION: [concise rationale]
            CONFLICTS: [list of unresolved discrepancies, if any]""",
            contexts_list=strategy_attempts
        )

        # STEP 5: COMPUTATIONAL VERIFICATION (IF APPLICABLE)
        # Extract final answer for verification
        answer_extraction = await self.generate(
            instruction="""Extract the final integer answer from the synthesis. If no clear integer, return "UNCLEAR".
            Also extract the key symbolic expression or equation that led to this answer.
            Output format: {"answer": "XXX", "verifiable_expression": "string or null"}""",
            context=synthesized
        )

        try:
            answer_data = json.loads(answer_extraction)
            if answer_data.get("answer") != "UNCLEAR" and answer_data.get("verifiable_expression"):
                # Verify via Programmer if a computable expression exists
                verification = await self.programmer(
                    instruction=f"""Verify the answer {answer_data['answer']} by computationally evaluating:
                    Expression: {answer_data['verifiable_expression']}
                    Constraints: Must yield integer result. Use exact arithmetic (fractions, radicals, modular arithmetic — NO FLOATS).
                    If result matches, output "VERIFIED: [answer]". If not, output "DISCREPANCY: computed=[value]".""",
                    context=synthesized,
                    max_retries=2
                )
                
                if "VERIFIED" in verification:
                    return answer_data['answer']
                else:
                    # Trigger lateral thinking if verification fails
                    lateral = await self.generate(
                        instruction=f"""Lateral thinking mode activated due to verification failure.
                        Reinterpret the problem using a completely different mathematical domain (e.g., if algebraic, try geometric; if combinatorial, try generating functions).
                        Derive answer from first principles. Ignore previous attempts. Output only the final integer answer.""",
                        context=""
                    )
                    return lateral.strip()
            else:
                return answer_data.get('answer', "000")
                
        except:
            # Fallback to synthesized answer if extraction fails
            final_answer = await self.generate(
                instruction="""Extract ONLY the final 3-digit integer answer from the synthesis. If none, return "000".
                Search for patterns like "FINAL_ANSWER: XXX" or boxed expressions. Be robust to formatting variations.""",
                context=synthesized
            )
            return final_answer.strip() or "000"