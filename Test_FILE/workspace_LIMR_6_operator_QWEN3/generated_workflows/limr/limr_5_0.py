# Workflow ID: limr_5_0
# Benchmark: limr
# Data Indices: [157, 46]

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

        # STEP 1: META-ANALYSIS — Classify problem type and strategy
        meta_analysis = await self.generate(
            instruction="""Perform deep meta-analysis of this mathematical problem:
            1. Classify the primary domain (combinatorics, number theory, algebra, geometry, probability, etc.)
            2. Identify required mathematical techniques (modular arithmetic, induction, coordinate geometry, etc.)
            3. Determine if the problem is decomposable or must be solved holistically
            4. Predict likely solution approaches (algebraic manipulation, combinatorial counting, recursive relation, etc.)
            5. Note any hidden constraints, edge cases, or deceptive elements
            6. Estimate computational complexity (light, medium, heavy)
            7. Suggest whether code execution will be necessary
            Format as a structured markdown report with clear section headers.""",
            context=""
        )

        # STEP 2: CONDITIONAL DECOMPOSITION — Only decompose if beneficial
        should_decompose = "decomposable" in meta_analysis.lower() or "subproblems" in meta_analysis.lower()
        subproblems = []
        if should_decompose:
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal, solvable subproblems.
                Each subproblem must:
                - Be mathematically well-defined
                - Have clear inputs and expected outputs
                - Be as independent as possible
                - Include any necessary context from the original problem
                Prioritize logical flow: earlier subproblems should feed into later ones.
                Return as list of subproblem dicts with 'id', 'description', 'dependencies'.""",
                context=meta_analysis
            )
            subproblems = decomposition
        else:
            # Treat as single atomic problem
            subproblems = [{
                "id": "MAIN",
                "description": "Solve the entire problem holistically",
                "dependencies": ""
            }]

        # STEP 3: PARALLEL SOLUTION EXPLORATION per subproblem
        final_subproblem_results = {}
        
        for subproblem in subproblems:
            sp_id = subproblem["id"]
            sp_desc = subproblem["description"]
            
            # Generate 3 parallel solution attempts using different mathematical lenses
            solution_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve subproblem {sp_id} using ALGEBRAIC/ANALYTICAL approach:
                    - Translate problem into equations or symbolic expressions
                    - Apply algebraic manipulation, substitutions, or transformations
                    - Show all steps rigorously
                    - Box final intermediate result
                    Subproblem: {sp_desc}""",
                    context=meta_analysis
                ),
                self.generate(
                    instruction=f"""Solve subproblem {sp_id} using COMBINATORIAL/ENUMERATIVE approach:
                    - Model as counting problem, use combinatorial principles
                    - Consider cases, symmetries, or recursive structures
                    - Avoid brute force unless necessary
                    - Box final intermediate result
                    Subproblem: {sp_desc}""",
                    context=meta_analysis
                ),
                self.generate(
                    instruction=f"""Solve subproblem {sp_id} using COMPUTATIONAL/ALGORITHMIC approach:
                    - Identify if this can be solved via code (counting, iteration, recursion, etc.)
                    - If yes, describe the algorithm precisely (to be handed to programmer later)
                    - If no, use geometric or probabilistic reasoning
                    - Box final intermediate result
                    Subproblem: {sp_desc}""",
                    context=meta_analysis
                )
            )

            # STEP 4: ITERATIVE REFINEMENT with verification (max 2 iterations)
            refined_attempts = []
            for attempt in solution_attempts:
                current = attempt
                for iteration in range(2):
                    verification = await self.generate(
                        instruction=f"""CRITICALLY VERIFY this solution attempt:
                        - Check for logical consistency
                        - Validate arithmetic and algebraic steps
                        - Test against edge cases or small examples
                        - Ensure answer format matches expectations (integer 000-999)
                        - Flag any uncertainties or assumptions
                        If errors found, explain precisely what's wrong.
                        If confident, state 'VERIFIED'.
                        Solution attempt: {current}""",
                        context=current
                    )
                    
                    if "verified" in verification.lower() and "error" not in verification.lower():
                        break
                    else:
                        current = await self.revise(
                            instruction=f"""REVISE based on verification feedback:
                            Feedback: {verification}
                            - Correct all identified errors
                            - Strengthen weak reasoning
                            - Add missing steps or justifications
                            - Maintain clear, step-by-step presentation""",
                            context=current
                        )
                refined_attempts.append(current)

            # STEP 5: ENSEMBLE SYNTHESIS for this subproblem
            subproblem_solution = await self.ensemble(
                instruction=f"""SYNTHESIZE these solution attempts for subproblem {sp_id}:
                - Compare methodologies and results
                - Resolve any conflicts by identifying root cause of discrepancy
                - If one approach is clearly superior, select it with justification
                - If multiple agree, synthesize into unified answer
                - Extract the final numerical result (must be integer 000-999)
                - If no consensus, pick most mathematically rigorous and explain uncertainty
                Format: 'FINAL ANSWER: [integer]' followed by justification.""",
                contexts_list=refined_attempts
            )
            final_subproblem_results[sp_id] = subproblem_solution

        # STEP 6: INTEGRATE SUBPROBLEM RESULTS (if multiple)
        if len(subproblems) > 1:
            integration_context = "\n\n".join([f"Subproblem {k}: {v}" for k,v in final_subproblem_results.items()])
            integrated_solution = await self.generate(
                instruction=f"""INTEGRATE these subproblem solutions into final answer:
                - Combine intermediate results according to logical dependencies
                - Perform any final calculations or transformations
                - Ensure consistency across subproblems
                - Output must be single integer between 000 and 999
                - If conflict remains, apply meta-reasoning from initial analysis
                Format: 'FINAL ANSWER: [integer]' with brief justification.
                Subproblem solutions: {integration_context}""",
                context=meta_analysis
            )
            final_output = integrated_solution
        else:
            final_output = list(final_subproblem_results.values())[0]

        # STEP 7: FINAL VALIDATION & EXTRACTION
        validated = await self.revise(
            instruction="""FINAL VALIDATION:
            - Extract the integer answer (must be 000-999)
            - Confirm it satisfies all original problem constraints
            - Recheck against any edge cases mentioned in meta-analysis
            - If answer is not integer or out of range, recompute
            - Output ONLY the 3-digit integer (e.g., '042', '123', '999')""",
            context=final_output
        )

        # STEP 8: PROGRAMMER FALLBACK for explicit computation (if needed)
        if "compute" in meta_analysis.lower() or "code" in meta_analysis.lower() or "algorithm" in meta_analysis.lower():
            try:
                code_result = await self.programmer(
                    instruction=f"""Generate and execute Python code to compute the final answer.
                    Based on this reasoning: {final_output}
                    - Must output single integer 000-999
                    - Handle edge cases explicitly
                    - No external libraries beyond standard math
                    - Return only the integer result""",
                    context=final_output,
                    max_retries=2
                )
                # Extract integer from code result if successful
                match = re.search(r'\b(\d{1,3})\b', code_result)
                if match:
                    final_int = int(match.group(1))
                    if 0 <= final_int <= 999:
                        validated = f"{final_int:03d}"
            except Exception:
                pass  # Fall back to previous validated answer

        return validated