# Workflow ID: limr_159_0
# Benchmark: limr
# Data Indices: [33, 272]

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

        # STEP 1: CLASSIFY PROBLEM TYPE AND STRATEGY
        classification = await self.generate(
            instruction="""Perform deep classification of this mathematical problem:
            1. Identify primary domain (algebra, number theory, combinatorics, geometry, etc.)
            2. Determine if it requires symbolic manipulation, numerical computation, or logical proof
            3. Assess whether brute-force computation is feasible (finite cases, small search space)
            4. Identify key mathematical objects (equations, sequences, geometric figures, modular constraints)
            5. Predict likely solution techniques (induction, generating functions, coordinate geometry, etc.)
            6. Flag any potential traps or non-obvious symmetries
            Output in structured JSON format with keys: domain, approach_type, computable, key_objects, techniques, traps""",
            context=""
        )

        # STEP 2: HIERARCHICAL DECOMPOSITION
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem into minimal solvable subproblems using this classification:
            {classification}
            
            Guidelines:
            - Each subproblem must be independently addressable
            - Specify dependencies clearly (what must be solved before what)
            - Include both computational and conceptual subproblems
            - At least one subproblem should be 'verify final answer'
            - Maximum 7 subproblems for manageability""",
            context=""
        )

        # STEP 3: PARALLEL STRATEGY EXPLORATION
        strategy_tasks = []
        strategy_names = [
            "algebraic_manipulation",
            "number_theoretic_approach",
            "combinatorial_reasoning",
            "geometric_interpretation",
            "computational_verification"
        ]

        for i, subproblem in enumerate(decomposition):
            sub_desc = subproblem['description']
            sub_id = subproblem['id']
            
            for strategy in strategy_names:
                task = self.generate(
                    instruction=f"""Solve subproblem {sub_id}: "{sub_desc}"
                    Using {strategy} approach:
                    - Show all intermediate steps
                    - Justify each transformation
                    - Note any assumptions made
                    - If stuck, explain why and suggest alternative
                    - Format final sub-result clearly""",
                    context=classification
                )
                strategy_tasks.append(task)

        # Execute all strategy attempts in parallel
        raw_strategy_results = await asyncio.gather(*strategy_tasks)

        # Group results by subproblem
        subproblem_results = {}
        idx = 0
        for i, subproblem in enumerate(decomposition):
            sub_id = subproblem['id']
            subproblem_results[sub_id] = raw_strategy_results[idx:idx+len(strategy_names)]
            idx += len(strategy_names)

        # STEP 4: META-VALIDATION AND CONSENSUS BUILDING
        final_sub_answers = {}
        
        for sub_id, results in subproblem_results.items():
            # Summarize each strategy result for clarity
            summarized_results = []
            for result in results:
                summary = await self.summarize(
                    instruction="Extract key conclusion and numerical result (if any). Ignore verbose steps. Max 50 words.",
                    context=result
                )
                summarized_results.append(summary)

            # Build consensus or flag contradiction
            consensus = await self.ensemble(
                instruction=f"""Analyze these {len(summarized_results)} solutions for subproblem {sub_id}:
                - If all agree, output the consensus answer
                - If contradictions exist, identify the most mathematically rigorous solution
                - If still uncertain, output 'CONTRADICTION' and list conflicting values
                - For proof-based subproblems, select the most complete logical argument
                - Final output must be a single clear answer or 'CONTRADICTION'""",
                contexts_list=summarized_results
            )

            # Handle contradictions with revision loop
            if "CONTRADICTION" in consensus:
                contradiction_resolution = await self.generate(
                    instruction=f"""Resolve contradiction in subproblem {sub_id}:
                    Conflicting results: {consensus}
                    Re-analyze from first principles.
                    Identify faulty assumptions in each conflicting approach.
                    Derive correct solution with step-by-step justification.
                    Output only the final correct answer for this subproblem.""",
                    context=f"Original subproblem: {subproblem['description']}"
                )
                final_sub_answers[sub_id] = contradiction_resolution
            else:
                final_sub_answers[sub_id] = consensus

        # STEP 5: COMPUTATIONAL VERIFICATION (IF APPLICABLE)
        computable_check = await self.generate(
            instruction=f"""Based on classification: {classification}
            Should we perform computational verification?
            Answer only 'YES' or 'NO'.""",
            context=""
        )

        if "YES" in computable_check.upper():
            try:
                verification_code = await self.generate(
                    instruction=f"""Generate Python code to verify the final answer.
                    Use the subproblem results: {json.dumps(final_sub_answers)}
                    Code must:
                    - Be self-contained
                    - Print only the final answer as integer
                    - Include assertions for intermediate checks
                    - Handle edge cases
                    - Run in under 5 seconds""",
                    context=""
                )
                
                verification_result = await self.programmer(
                    instruction="Execute verification code and return result",
                    context=verification_code,
                    max_retries=2
                )
                
                # Integrate verification result
                verification_summary = await self.summarize(
                    instruction="Extract final verified answer from code output. If error, return 'VERIFICATION_FAILED'",
                    context=verification_result
                )
                
                if "VERIFICATION_FAILED" not in verification_summary:
                    # Update final answer with verified result
                    final_sub_answers['verification'] = verification_summary
            except Exception:
                pass  # Silently fail if verification not possible

        # STEP 6: SYNTHESIZE FINAL ANSWER
        synthesis_input = "\n".join([f"Subproblem {k}: {v}" for k, v in final_sub_answers.items()])
        
        final_answer_draft = await self.generate(
            instruction=f"""Synthesize final answer from subproblem results:
            {synthesis_input}
            
            Requirements:
            - The answer must be an integer between 000 and 999
            - Show how subproblem results combine to form final answer
            - Justify why this is the only possible answer
            - If multiple answers possible, list all and explain
            - Format: "FINAL_ANSWER: <integer>" on last line""",
            context=""
        )

        # STEP 7: RIGOROUS REVISION AND FORMATTING
        final_answer = await self.revise(
            instruction="""Revise for:
            1. Mathematical correctness - verify all steps
            2. Precision - ensure integer answer format
            3. Clarity - remove unnecessary verbosity
            4. Compliance - answer must be 000-999 integer
            5. Final line must be exactly "FINAL_ANSWER: <integer>"
            If any doubt remains, re-derive from first principles.""",
            context=final_answer_draft
        )

        # STEP 8: EXTRACTION AND RETURN
        extraction = await self.generate(
            instruction="""Extract ONLY the final integer answer from this text.
            Look for line starting with "FINAL_ANSWER: "
            Return ONLY the 3-digit integer (with leading zeros if needed).
            If uncertain, return "000" as fallback.""",
            context=final_answer
        )

        return extraction.strip()