# Workflow ID: limr_61_0
# Benchmark: limr
# Data Indices: [100, 160]

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

        # STEP 1: CLASSIFY PROBLEM & GENERATE PARALLEL HYPOTHESES
        classification = await self.generate(
            instruction="""Perform deep problem classification. Analyze the problem and answer these questions:
            1. What primary mathematical domain does this belong to? (Algebra, Number Theory, Combinatorics, Geometry, Probability, Optimization, Sequences)
            2. What secondary domains are involved?
            3. What is the estimated solution complexity? (Low: direct formula, Medium: 2-3 steps, High: non-obvious insight or multi-step proof)
            4. Are there explicit constraints or edge cases mentioned?
            5. What form must the answer take? (Always an integer 0-999, but note any special formatting)
            6. List all named variables, constants, and their relationships.
            7. Suggest 3 distinct solution strategies from different mathematical perspectives.
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY EXPLORATION
        strategy_instructions = [
            """Adopt an ALGEBRAIC/ANALYTICAL lens. Assume the problem is best solved by:
            - Setting up equations or functions
            - Applying algebraic manipulation or calculus
            - Solving for unknowns symbolically
            Develop a complete solution path under this assumption. Show all steps. If you hit a dead end, explain why.""",
            
            """Adopt a COMBINATORIAL/NUMBER THEORETIC lens. Assume the problem is best solved by:
            - Counting principles, modular arithmetic, or divisibility
            - Case analysis or recursive thinking
            - Prime factorization or Diophantine reasoning
            Develop a complete solution path under this assumption. Show all steps. If you hit a dead end, explain why.""",
            
            """Adopt a GEOMETRIC/OPTIMIZATION lens. Assume the problem is best solved by:
            - Coordinate geometry, vector analysis, or spatial reasoning
            - Maximization/minimization via inequalities or calculus
            - Symmetry or transformation arguments
            Develop a complete solution path under this assumption. Show all steps. If you hit a dead end, explain why."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # STEP 3: ENSEMBLE SYNTHESIS & STRATEGY SELECTION
        synthesized_strategy = await self.ensemble(
            instruction="""You are a senior mathematician reviewing three solution attempts from different perspectives.
            Your task:
            1. Identify which approach is most promising and mathematically sound.
            2. Extract the strongest insights from each attempt.
            3. Synthesize a unified solution plan that combines the best elements.
            4. Flag any inconsistencies, errors, or unverified assumptions.
            5. Explicitly state the final recommended approach and why.
            Output a coherent, step-by-step solution roadmap.""",
            contexts_list=strategy_attempts
        )

        # STEP 4: CONDITIONAL DECOMPOSITION (if complexity is high)
        decomposition = None
        if "High" in classification or "multi-step" in classification.lower() or "proof" in classification.lower():
            try:
                decomposition = await self.decompose(
                    instruction="""Break down the synthesized solution plan into atomic, executable subproblems.
                    Requirements:
                    - Each subproblem must be solvable independently once dependencies are met.
                    - Specify exact mathematical operations or reasoning steps required.
                    - Include validation criteria for each subproblem's output.
                    - Order subproblems by dependency (prerequisites first).
                    - Maximum 7 subproblems; if more are needed, group related steps.""",
                    context=synthesized_strategy
                )
            except Exception:
                # Fallback: proceed without decomposition if it fails
                decomposition = None

        # STEP 5: EXECUTE SOLUTION (with decomposition if available)
        if decomposition:
            # Execute subproblems in dependency order
            subproblem_results = {}
            for sub in decomposition:
                dep_ids = sub.get('dependencies', '').split(',') if sub.get('dependencies') else []
                # Wait for dependencies (simplified: execute sequentially in list order)
                # In a more advanced version, we'd build a DAG and execute in topological order
                context_for_sub = "\n".join([f"Subproblem {did}: {subproblem_results.get(did, '')}" 
                                           for did in dep_ids if did in subproblem_results])
                
                sub_attempt = await self.generate(
                    instruction=f"""Solve this subproblem as part of a larger solution:
                    {sub['description']}
                    Use the following context from prerequisite subproblems:
                    {context_for_sub}
                    Show all work. Box your final answer for this subproblem.""",
                    context=synthesized_strategy
                )
                
                # Validate subproblem result
                validated_sub = await self.revise(
                    instruction="""Critically review this subproblem solution:
                    - Verify all calculations and logical steps.
                    - Check consistency with prerequisite results.
                    - Ensure no steps are skipped or assumed.
                    - If error found, correct it and explain the fix.
                    Output only the corrected solution.""",
                    context=sub_attempt
                )
                subproblem_results[sub['id']] = validated_sub

            # Combine subproblem results into final answer
            final_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in subproblem_results.items()])
            combined_solution = await self.generate(
                instruction="""Synthesize all subproblem results into a final answer.
                - Reconstruct the complete logical flow.
                - Ensure all dependencies are satisfied.
                - Extract the final numerical answer (integer 0-999).
                - Double-check against original problem constraints.
                Output ONLY the final integer answer, nothing else.""",
                context=final_context
            )
        else:
            # Direct solution without decomposition
            direct_solution = await self.generate(
                instruction="""Execute the synthesized solution plan end-to-end.
                - Show all mathematical steps clearly.
                - Justify non-obvious insights or transformations.
                - Verify intermediate results where possible.
                - Extract the final numerical answer (integer 0-999).
                Output ONLY the final integer answer, nothing else.""",
                context=synthesized_strategy
            )
            
            # Validate and refine
            validated_solution = await self.revise(
                instruction="""You are a ruthless math competition grader.
                - Scrutinize every step for errors.
                - Check boundary conditions and edge cases.
                - Verify the answer is an integer between 0 and 999.
                - If any flaw is found, correct it and show the fix.
                Output ONLY the corrected final integer answer.""",
                context=direct_solution
            )
            combined_solution = validated_solution

        # STEP 6: FINAL SANITIZATION & OUTPUT
        final_answer = await self.revise(
            instruction="""Extract ONLY the final integer answer from the text below.
            - Remove all explanatory text, units, or formatting.
            - Ensure it's an integer between 0 and 999.
            - If multiple numbers exist, select the one that answers the original question.
            - If no valid integer exists, output '000'.
            Output ONLY the three-digit integer (e.g., '042', '123', '999').""",
            context=combined_solution
        )

        # Clean and return
        # Extract first 1-3 digit number
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 999:
                return f"{num:03d}" if num < 100 else str(num)
        
        # Fallback
        return "000"