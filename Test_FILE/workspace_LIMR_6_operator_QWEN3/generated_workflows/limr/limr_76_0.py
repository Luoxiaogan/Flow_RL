# Workflow ID: limr_76_0
# Benchmark: limr
# Data Indices: [35, 39]

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
        import re

        # STEP 1: META-ANALYSIS — Understand problem structure and recommend strategies
        meta_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this mathematical problem. Identify:
            1. Problem category (algebra, number theory, combinatorics, geometry, etc.)
            2. Key variables, constraints, and target expressions
            3. Hidden symmetries, substitutions, or transformations that could simplify it
            4. Potential solution strategies (at least 3 distinct approaches)
            5. Known pitfalls or common mistakes for this problem type
            6. Whether numerical computation or symbolic manipulation is more appropriate
            7. Expected form of the answer (integer, expression, etc.)
            
            Format your response as a structured report with clear section headers.""",
            context=""
        )

        # STEP 2: GENERATE MULTIPLE SOLUTION STRATEGIES IN PARALLEL
        strategy_instructions = [
            """Develop a complete solution using ALGEBRAIC MANIPULATION. 
            Focus on equation rearrangement, substitution, factoring, and exploiting symmetries.
            Show every step with justification. Assume nothing — verify each transformation.
            If stuck, hypothesize and test potential simplifications.""",
            
            """Develop a complete solution using FUNCTIONAL or GRAPHICAL INTUITION.
            Consider behavior of functions, monotonicity, bounds, or geometric interpretations.
            Sketch conceptual graphs or transformations if helpful. Use inequalities or extremal reasoning.
            Convert abstract expressions into visual or intuitive models.""",
            
            """Develop a complete solution using COMPUTATIONAL or ALGORITHMIC APPROACH.
            Design a step-by-step algorithm or numerical procedure. Consider iteration, recursion, or brute-force with pruning.
            Identify computational bottlenecks and optimize. Prepare for potential code implementation.""",
            
            """Develop a solution using NUMBER THEORETIC or COMBINATORIAL REASONING.
            Look for divisibility, modular patterns, prime factors, counting principles, or combinatorial identities.
            Apply generating functions, pigeonhole principle, or inclusion-exclusion if relevant.""",
            
            """Develop a solution by ANALOGY or TRANSFORMATION.
            Map this problem to a known theorem, standard form, or previously solved problem.
            Use change of variables, coordinate transforms, or isomorphisms to reduce complexity.
            Leverage known identities or inequalities (AM-GM, Cauchy-Schwarz, etc.) if applicable."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=meta_analysis) for instr in strategy_instructions]
        )

        # STEP 3: DECOMPOSE EACH STRATEGY INTO VERIFIABLE SUBPROBLEMS
        decomposed_strategies = []
        for i, attempt in enumerate(strategy_attempts):
            try:
                decomposition = await self.decompose(
                    instruction=f"""Break down this solution attempt into atomic, verifiable subproblems.
                    Each subproblem should be self-contained and checkable in isolation.
                    Include dependencies if steps rely on prior results.
                    Focus on isolating potential error points: algebraic manipulations, domain assumptions, boundary conditions.
                    Return as list of subproblem dictionaries with 'id', 'description', 'dependencies'.""",
                    context=attempt
                )
                decomposed_strategies.append({
                    'original_attempt': attempt,
                    'decomposition': decomposition,
                    'strategy_index': i
                })
            except Exception:
                # Fallback: treat whole attempt as single subproblem
                decomposed_strategies.append({
                    'original_attempt': attempt,
                    'decomposition': [{
                        'id': 'fallback_0',
                        'description': 'Full solution attempt (decomposition failed)',
                        'dependencies': ''
                    }],
                    'strategy_index': i
                })

        # STEP 4: ITERATIVE REFINEMENT LOOP WITH ADVERSARIAL VALIDATION
        refined_solutions = []
        for strategy in decomposed_strategies:
            current_solution = strategy['original_attempt']
            subproblems = strategy['decomposition']
            
            # Process each subproblem with validation
            for subprob in subproblems:
                for iteration in range(3):  # Max 3 refinement iterations
                    # Validate this step adversarially
                    validation = await self.generate(
                        instruction=f"""CRITICALLY EXAMINE THIS STEP:
                        "{subprob['description']}"
                        
                        Assume it contains a subtle error. Hunt for:
                        - Algebraic mistakes (sign errors, incorrect expansions)
                        - Domain violations (division by zero, invalid roots)
                        - Logical gaps (unjustified assumptions)
                        - Boundary condition oversights
                        - Extraneous or missing solutions
                        
                        If no error found, state "NO ERROR FOUND". Otherwise, describe the flaw precisely.""",
                        context=current_solution
                    )
                    
                    if "NO ERROR FOUND" not in validation.upper():
                        # Revise the solution based on critique
                        current_solution = await self.revise(
                            instruction=f"""Fix the following critique in the solution:
                            Critique: {validation}
                            
                            Preserve correct parts. Only modify flawed sections.
                            Add explicit justifications for corrected steps.
                            Maintain mathematical rigor and precision.""",
                            context=current_solution
                        )
                    else:
                        break  # No error found, move to next subproblem
            
            refined_solutions.append(current_solution)

        # STEP 5: ENSEMBLE SYNTHESIS — COMBINE BEST ELEMENTS
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from all refined attempts. Criteria:
            1. Prefer solutions that passed adversarial validation without revisions
            2. Favor elegance and minimal assumptions
            3. Prioritize solutions with clear, verifiable steps
            4. If multiple solutions agree numerically, choose the most insightful
            5. If solutions conflict, trace back to first point of divergence and select the most rigorously justified path
            6. Extract the final numerical answer (integer between 000-999) and highlight it clearly
            
            Output format: 
            [SYNTHESIZED SOLUTION]
            ... detailed steps ...
            FINAL ANSWER: [integer]""",
            contexts_list=refined_solutions
        )

        # STEP 6: PROGRAMMATIC VERIFICATION — NUMERICAL SANITY CHECK
        try:
            verification_result = await self.programmer(
                instruction=f"""Generate Python code to numerically verify the final answer from this solution:
                {final_solution}
                
                Requirements:
                - Implement exact computation (no floating point if avoidable)
                - Check all constraints and boundary conditions
                - Test for extraneous solutions
                - Output should be the verified integer answer or 'ERROR' if verification fails
                - Include comprehensive comments explaining the verification logic""",
                context=final_solution,
                max_retries=3
            )
            
            # Extract verified answer if possible
            verified_answer_match = re.search(r'(?:FINAL ANSWER|output|result)[^\d]*(\d{1,3})', verification_result, re.IGNORECASE)
            if verified_answer_match:
                verified_answer = verified_answer_match.group(1).zfill(3)  # Ensure 3-digit format
                final_solution += f"\n\nPROGRAMMATIC VERIFICATION CONFIRMS: {verified_answer}"
        except Exception:
            # Verification failed — proceed with symbolic solution but note the issue
            final_solution += "\n\nWARNING: Programmatic verification failed — relying on symbolic solution."

        # STEP 7: META-VALIDATION — FINAL SKEPTICAL REVIEW
        meta_validation = await self.generate(
            instruction="""You are a world-class mathematician grading this solution harshly.
            Critique it as if it were submitted to the IMO. Look for:
            - Any remaining logical gaps
            - Overlooked edge cases
            - Lack of rigor in justification
            - Formatting or clarity issues
            - Whether the final answer is properly boxed and justified
            
            If no significant issues, respond with "SOLUTION IS RIGOROUS". Otherwise, list flaws.""",
            context=final_solution
        )

        if "SOLUTION IS RIGOROUS" not in meta_validation.upper():
            final_solution = await self.revise(
                instruction=f"""Address the following critique from expert review:
                {meta_validation}
                
                Strengthen justifications, close logical gaps, and improve clarity.
                Preserve the core solution but elevate its rigor to competition standards.
                Ensure final answer is prominently displayed and unambiguous.""",
                context=final_solution
            )

        # Extract and return final answer in required format
        answer_match = re.search(r'(?:FINAL ANSWER|answer|result)[^\d]*(\d{1,3})', final_solution, re.IGNORECASE)
        if answer_match:
            final_answer = answer_match.group(1).zfill(3)
        else:
            # Fallback: return first 3-digit number found
            fallback_match = re.search(r'\b\d{1,3}\b', final_solution)
            final_answer = fallback_match.group(0).zfill(3) if fallback_match else "000"

        return final_answer