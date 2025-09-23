# Workflow ID: limr_114_0
# Benchmark: limr
# Data Indices: [147, 76]

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

        # Step 1: Meta-Analysis - Understand problem type and strategize
        strategy_analysis = await self.generate(
            instruction="""You are a world-class mathematical problem solver preparing for the International Mathematical Olympiad.
            Analyze the given problem with extreme depth and classify it:

            1. Primary Domain: Is this primarily algebra, number theory, combinatorics, geometry, or probability?
            2. Solution Style: Does it require symbolic manipulation, combinatorial counting, geometric insight, computational enumeration, or proof?
            3. Key Insight: What is the likely 'trick' or non-obvious observation needed? (e.g., symmetry, substitution, invariant, combinatorial identity)
            4. Computational Feasibility: Can this be brute-forced with code? (e.g., small finite sets, explicit enumeration)
            5. Decomposability: Can this be broken into independent subproblems? If so, list them.

            Format your response as a structured JSON-like analysis with clear sections. Be brutally honest about difficulty and potential pitfalls.""",
            context=""
        )

        # Step 2: Attempt decomposition (if applicable)
        decomposition_attempt = await self.decompose(
            instruction="""Based on the problem structure, break it down into the smallest meaningful subproblems.
            Each subproblem should be solvable independently or with specified dependencies.
            If the problem is atomic (cannot be meaningfully decomposed), return a single subproblem.
            Format each subproblem with clear, actionable description and dependencies.""",
            context=strategy_analysis
        )

        # Step 3: Parallel Solution Exploration - Launch multiple approaches simultaneously
        # Approach 1: Symbolic/Algebraic Reasoning
        symbolic_approach = asyncio.create_task(
            self.generate(
                instruction=f"""You are an expert algebraist. Solve the problem using symbolic manipulation, identities, and mathematical insights.
                Leverage the analysis: {strategy_analysis[:1000]}
                
                Guidelines:
                - Use substitutions, symmetries, or transformations to simplify.
                - Reference known theorems or identities if applicable.
                - Show all steps clearly.
                - Verify intermediate results against problem constraints.
                - Final answer must be an integer between 000 and 999.
                """,
                context=""
            )
        )

        # Approach 2: Computational/Programmatic Solution (if feasible)
        computational_approach = asyncio.create_task(
            self.programmer(
                instruction=f"""Generate Python code to solve the problem computationally.
                Consider: {strategy_analysis[:800]}
                
                Requirements:
                - Handle edge cases and constraints explicitly.
                - If combinatorial, use itertools or explicit loops.
                - If algebraic, use sympy only if necessary.
                - Output must be a single integer 000-999.
                - Include verification step if possible.
                """,
                context="",
                max_retries=2
            )
        )

        # Approach 3: Step-by-Step Decomposed Solution (if decomposition is meaningful)
        if len(decomposition_attempt) > 1 or (len(decomposition_attempt) == 1 and "atomic" not in decomposition_attempt[0]['description'].lower()):
            # Build solution by solving subproblems in dependency order
            solved_subproblems = {}
            for subproblem in decomposition_attempt:
                deps = subproblem.get('dependencies', "").split(',') if subproblem.get('dependencies') else []
                # Wait for dependencies (simplified - in practice, topological sort needed)
                dep_context = "\n".join([f"Subproblem {d}: {solved_subproblems.get(d, 'Not solved yet')}" for d in deps if d in solved_subproblems])
                
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem as part of a larger solution:
                    Subproblem: {subproblem['description']}
                    Dependencies: {dep_context}
                    
                    Use precise mathematical reasoning. Show all steps. Your output will be integrated into a larger solution.""",
                    context=dep_context
                )
                solved_subproblems[subproblem['id']] = sub_solution
            
            # Integrate subproblem solutions
            decomposed_solution = await self.generate(
                instruction=f"""Integrate the following subproblem solutions into a complete answer:
                {json.dumps(solved_subproblems, indent=2)}
                
                Ensure consistency and derive the final integer answer (000-999).""",
                context=json.dumps(solved_subproblems)
            )
        else:
            # Fallback: treat as atomic
            decomposed_solution = await self.generate(
                instruction=f"""Solve the problem holistically, as it cannot be meaningfully decomposed.
                Analysis: {strategy_analysis[:1000]}
                Show all steps. Final answer must be integer 000-999.""",
                context=""
            )

        # Gather parallel results
        symbolic_result, computational_result = await asyncio.gather(symbolic_approach, computational_approach)
        
        # Step 4: Critique and Revise each solution attempt
        revised_symbolic = await self.revise(
            instruction="""Critically review this solution. Assume it contains at least one subtle error.
            - Check algebraic manipulations step by step.
            - Verify against original problem constraints.
            - Ensure final answer is integer 000-999.
            - If error found, correct it. If confident, state 'VERIFIED'.
            Output the corrected solution with verification note.""",
            context=symbolic_result
        )

        revised_computational = await self.revise(
            instruction="""Review this computational solution:
            - Does the code logic match the problem?
            - Are edge cases handled?
            - Does output format match requirement (single integer 000-999)?
            - If code failed, explain why and suggest symbolic alternative.
            Output corrected code or revised reasoning.""",
            context=computational_result
        )

        revised_decomposed = await self.revise(
            instruction="""Review this decomposed solution:
            - Are subproblems solved correctly?
            - Is integration of sub-solutions logically sound?
            - Does final answer satisfy original problem?
            - Correct any errors and verify final integer output.
            Output revised complete solution.""",
            context=decomposed_solution
        )

        # Step 5: Ensemble - Synthesize best answer from multiple approaches
        final_answer = await self.ensemble(
            instruction="""You are the final arbiter of mathematical truth. Evaluate these three solution attempts:
            1. Symbolic Approach (revised)
            2. Computational Approach (revised)
            3. Decomposed Approach (revised)

            Criteria:
            - Mathematical correctness and rigor
            - Alignment with problem constraints
            - Clarity and verifiability of steps
            - Final answer as integer 000-999

            If all agree, output the consensus answer.
            If conflict, perform meta-analysis: which approach is most reliable for this problem type?
            Output ONLY the final 3-digit integer answer (e.g., '456'), nothing else.""",
            contexts_list=[revised_symbolic, revised_computational, revised_decomposed]
        )

        # Step 6: Final Verification - Reverse engineer from answer
        verification = await self.generate(
            instruction=f"""Given the candidate answer: {final_answer}
            Verify it by reverse-engineering:
            - Plug this answer back into the original problem.
            - Does it satisfy all conditions?
            - If not, what went wrong? (But do not change answer unless catastrophic error)
            - Output 'VERIFIED' or 'UNVERIFIED - [reason]'""",
            context=final_answer
        )

        # If unverified, attempt one last revision
        if "UNVERIFIED" in verification:
            final_answer = await self.revise(
                instruction=f"""The answer {final_answer} failed verification: {verification}
                Re-solve the problem from scratch with extreme caution.
                Use the most reliable method identified earlier.
                Output ONLY the 3-digit integer answer.""",
                context=strategy_analysis
            )

        return final_answer.strip()