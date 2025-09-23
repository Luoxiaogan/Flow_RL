# Workflow ID: limr_6_0
# Benchmark: limr
# Data Indices: [9, 178]

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

        # === PHASE 1: META-ANALYSIS & STRATEGY HYPOTHESIS ===
        strategy_hypothesis = await self.generate(
            instruction="""Perform deep problem classification and strategy generation:
            1. Identify the mathematical domain (algebra, number theory, combinatorics, geometry, etc.) and sub-domain.
            2. List 3 distinct solution strategies that could apply. For each strategy:
               - Describe the core mathematical insight or transformation required
               - Explain why this approach might be promising
               - Outline potential subproblems or computational steps
               - Identify known pitfalls or failure modes for this approach
            3. Prioritize strategies by estimated likelihood of success and elegance.
            4. Format output as a numbered list with clear section headers.""",
            context=""
        )

        # === PHASE 2: PARALLEL STRATEGY EXPLORATION ===
        # Extract strategy list (simplified parsing - in practice, use more robust extraction)
        strategy_lines = [s.strip() for s in strategy_hypothesis.split('\n') if s.strip().startswith(('1.', '2.', '3.'))]
        strategies = strategy_lines[:3]  # Take top 3

        async def explore_strategy(strategy_desc: str, idx: int):
            """Explore one strategy end-to-end with validation"""
            try:
                # Step 2a: Decompose according to this strategy
                decomposition = await self.decompose(
                    instruction=f"""Decompose the problem using this strategy: {strategy_desc}
                    Break it into minimal, logically ordered subproblems. For each subproblem:
                    - State what needs to be solved
                    - Specify dependencies on other subproblems
                    - Indicate whether it requires symbolic reasoning, computation, or both
                    Return as list of subproblem dictionaries.""",
                    context=strategy_desc
                )

                # Step 2b: Generate solution draft following decomposition
                solution_draft = await self.generate(
                    instruction=f"""Develop a complete solution following this decomposition: {json.dumps(decomposition, indent=2)}
                    For each subproblem in order:
                    - Show all mathematical steps
                    - Justify key insights or transformations
                    - Flag any uncertain or risky steps
                    - Propose how to verify each step computationally if applicable
                    Maintain full mathematical rigor and precision.""",
                    context=strategy_desc
                )

                # Step 2c: Revise for rigor and completeness
                refined_solution = await self.revise(
                    instruction="""Critically review this solution:
                    - Verify logical consistency and mathematical correctness
                    - Check for missing cases or edge conditions
                    - Ensure all variables are properly defined and constrained
                    - Improve clarity and add explanatory notes where needed
                    - Explicitly state any assumptions made
                    Output the revised solution with corrections clearly marked.""",
                    context=solution_draft
                )

                # Step 2d: Computational verification of key steps
                # Extract computational tasks (simplified - in practice, use regex or LLM extraction)
                computational_verification = await self.programmer(
                    instruction=f"""Identify and execute computational verifications for critical steps in this solution: {refined_solution}
                    - Compute any numerical values, sums, or expressions
                    - Verify inequalities or equalities with sample values
                    - Check boundary conditions or edge cases numerically
                    - Return results with clear labels matching solution steps""",
                    context=refined_solution,
                    max_retries=2
                )

                # Step 2e: Validation - try to break the solution
                validation_report = await self.generate(
                    instruction=f"""Attempt to falsify this solution: {refined_solution}
                    - Look for logical gaps, unstated assumptions, or calculation errors
                    - Test edge cases, boundary values, or special conditions
                    - Consider alternative interpretations of the problem statement
                    - If flaws are found, describe them precisely. If none, state 'VALIDATED'.
                    Be brutally honest - this is a peer review.""",
                    context=refined_solution
                )

                # Step 2f: Final revision incorporating validation
                if "flaw" in validation_report.lower() or "error" in validation_report.lower():
                    final_solution = await self.revise(
                        instruction=f"""Incorporate these validation findings: {validation_report}
                        Fix all identified issues while preserving the core approach.
                        If the approach is fundamentally flawed, state 'STRATEGY_FAILED' at the start.""",
                        context=refined_solution
                    )
                else:
                    final_solution = refined_solution + "\n\n=== VALIDATION PASSED ==="

                return {
                    'strategy': strategy_desc,
                    'solution': final_solution,
                    'verification': computational_verification,
                    'validation': validation_report,
                    'index': idx
                }
            except Exception as e:
                return {
                    'strategy': strategy_desc,
                    'solution': f"ERROR: {str(e)}",
                    'verification': "",
                    'validation': "FAILED_DUE_TO_EXCEPTION",
                    'index': idx
                }

        # Run all strategies in parallel
        strategy_results = await asyncio.gather(
            *[explore_strategy(strat, i) for i, strat in enumerate(strategies)]
        )

        # === PHASE 3: SYNTHESIS & SELECTION ===
        # Filter out failed strategies
        valid_solutions = [
            res for res in strategy_results 
            if "STRATEGY_FAILED" not in res['solution'] and "ERROR" not in res['solution']
        ]

        if not valid_solutions:
            # Fallback: Pivot based on failure analysis
            failure_analysis = await self.summarize(
                instruction="""Analyze why all strategies failed:
                - What common pitfalls or misconceptions emerged?
                - What aspects of the problem were most challenging?
                - What new approaches might overcome these failures?
                Generate 2 new strategy hypotheses based on these insights.""",
                context=json.dumps(strategy_results, indent=2)
            )
            
            # Simple fallback solution attempt
            final_answer = await self.generate(
                instruction=f"""Given previous failures: {failure_analysis}
                Attempt one last solution using the most promising new approach.
                Focus on computational verification and extreme simplicity.
                Output only the final integer answer between 000 and 999.""",
                context=failure_analysis
            )
        else:
            # Ensemble selection from valid solutions
            final_answer = await self.ensemble(
                instruction="""Select the best solution from these candidates:
                - Prioritize mathematical rigor and completeness
                - Favor solutions with successful computational verification
                - Prefer elegant, insightful approaches over brute force
                - Ensure the final answer is an integer between 000 and 999
                - If multiple solutions agree, that increases confidence
                - Extract and output ONLY the final numerical answer in 3-digit format (e.g., 042)""",
                contexts_list=[res['solution'] + "\n\nVERIFICATION: " + res['verification'] for res in valid_solutions]
            )

        # === PHASE 4: FINAL VALIDATION & FORMATTING ===
        # Ensure output is clean 3-digit integer
        clean_answer = await self.revise(
            instruction="""Format this as a 3-digit integer between 000 and 999:
            - Extract only the numerical answer
            - Remove any text, units, or explanations
            - Pad with leading zeros if necessary (e.g., 42 becomes 042)
            - If multiple numbers, select the one that answers the original question
            - If no valid number, return '000'""",
            context=final_answer
        )

        return clean_answer.strip()