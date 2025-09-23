# Workflow ID: limr_135_0
# Benchmark: limr
# Data Indices: [222, 287]

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

        # === PHASE 1: META-STRATEGY TRIAGE ===
        # Generate parallel strategic perspectives before diving into solution
        strategy_prompts = [
            """Analyze the most straightforward, brute-force computational approach to this problem. 
            What direct calculations, enumerations, or algorithmic methods could yield the answer? 
            Identify computational bottlenecks and feasibility concerns. Be brutally honest about complexity.""",
            
            """Analyze the most elegant, insight-driven mathematical approach. 
            What theorems, transformations, or conceptual leaps could simplify or bypass computation? 
            Focus on structural properties, symmetries, or domain-specific insights (number theory, combinatorics, etc.).""",
            
            """Identify the most error-prone aspects and common pitfalls. 
            What assumptions are tempting but dangerous? What edge cases are easily overlooked? 
            What 'obvious' approaches lead to wrong answers? Generate a pre-mortem of failure modes."""
        ]
        
        meta_strategies = await asyncio.gather(
            *[self.generate(instruction=prompt, context="") for prompt in strategy_prompts]
        )
        
        # Synthesize meta-strategies into a unified attack plan
        attack_plan = await self.ensemble(
            instruction="""Synthesize these three strategic perspectives into a unified solution plan:
            1. Leverage the elegance from perspective 2 to avoid brute-force complexity from perspective 1
            2. Embed the cautionary insights from perspective 3 as validation checkpoints
            3. Prioritize approaches that yield exact integer answers (000-999) with minimal computational risk
            4. Structure the plan as a sequence of verifiable steps with fallback options
            Output a clear, step-by-step strategy document.""",
            contexts_list=meta_strategies
        )

        # === PHASE 2: HIERARCHICAL DECOMPOSITION ===
        # Break problem into subproblems with domain tagging
        decomposition = await self.decompose(
            instruction=f"""Decompose the problem using this strategic plan:
            {attack_plan}
            
            For each subproblem:
            - Tag its mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            - Estimate its solvability (trivial, moderate, hard, requires insight)
            - Identify dependencies between subproblems
            - Flag any subproblem that matches known failure modes from the meta-strategy
            Output structured subproblems with these annotations.""",
            context=attack_plan
        )

        # === PHASE 3: PARALLEL SUBPROBLEM SOLVING ===
        # Solve each subproblem with domain-aware instructions
        async def solve_subproblem(subproblem):
            domain = subproblem.get('domain', 'general')
            description = subproblem['description']
            
            domain_instructions = {
                'number theory': """Apply number theory techniques: modular arithmetic, divisibility rules, 
                prime factorization, Diophantine analysis. Check for patterns in small cases first. 
                Verify solutions satisfy original constraints exactly.""",
                
                'combinatorics': """Apply combinatorial principles: counting, permutations, combinations, 
                inclusion-exclusion. Watch for overcounting/undercounting. Verify with small cases. 
                Ensure integer results - fractional answers indicate errors.""",
                
                'algebra': """Apply algebraic manipulation: equation solving, substitution, symmetry exploitation. 
                Check for extraneous solutions. Verify by plugging back into original equations.""",
                
                'geometry': """Apply geometric principles: coordinate geometry, vector analysis, symmetry. 
                Verify with multiple approaches if possible. Check dimensional consistency.""",
                
                'optimization': """Apply optimization techniques: inequalities, calculus (if applicable), 
                boundary analysis. Verify global vs local extrema. Check integer constraints."""
            }
            
            base_instruction = f"""Solve this subproblem: {description}
            Mathematical domain: {domain}
            
            {domain_instructions.get(domain, 'Apply appropriate mathematical techniques for this domain.')}
            
            CRITICAL: Output must be precise, step-by-step reasoning leading to an exact value or expression. 
            If stuck, identify what's missing and request recursive decomposition."""
            
            # First attempt
            solution = await self.generate(instruction=base_instruction, context="")
            
            # Verification loop
            for attempt in range(3):
                verification = await self.generate(
                    instruction=f"""Adversarial verification: Assume this solution is WRONG. 
                    What are the most likely errors? Check:
                    - Arithmetic mistakes
                    - Logical gaps
                    - Domain-specific pitfalls (e.g., modular constraints, combinatorial overcounting)
                    - Consistency with original problem constraints
                    If no errors found, output 'VERIFIED'. Otherwise, list specific errors.""",
                    context=solution
                )
                
                if "VERIFIED" in verification.upper():
                    break
                else:
                    solution = await self.revise(
                        instruction=f"""Fix these specific errors: {verification}
                        Maintain all correct parts. Add explicit verification steps for each claim.
                        Output revised solution with error corrections highlighted.""",
                        context=solution
                    )
            
            return solution

        # Solve all subproblems in parallel
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in decomposition]
        )

        # === PHASE 4: SYNTHESIS AND CROSS-VERIFICATION ===
        # Combine subproblem solutions into final answer
        synthesis = await self.ensemble(
            instruction="""Synthesize these subproblem solutions into a complete answer:
            1. Integrate results in dependency order
            2. Verify consistency between subproblem solutions
            3. Resolve any contradictions by revisiting original constraints
            4. Output final answer as an integer between 000 and 999
            5. Include brief justification showing how all constraints are satisfied""",
            contexts_list=subproblem_solutions
        )

        # === PHASE 5: ADVERSARIAL FINAL VALIDATION ===
        # Final sanity check with adversarial perspective
        final_validation = await self.generate(
            instruction=f"""Final adversarial validation: Assume this answer is INCORRECT.
            {synthesis}
            
            What is the most plausible correct answer and why? 
            What subtle detail might have been missed? 
            Re-examine original problem constraints for any oversight.
            If you cannot find a flaw, output 'CONFIRMED: [answer]'. 
            If you find a potential flaw, output 'REVISION NEEDED: [explanation]'.""",
            context=synthesis
        )

        if "REVISION NEEDED" in final_validation:
            # One last revision attempt
            synthesis = await self.revise(
                instruction=f"""Address this final concern: {final_validation}
                Re-verify all steps. Output final answer as integer 000-999 with complete justification.""",
                context=synthesis
            )

        # Extract final answer (ensure it's an integer 000-999)
        final_answer = await self.programmer(
            instruction="""Extract the final integer answer from this solution.
            The answer must be an integer between 000 and 999.
            If multiple candidates exist, select the one that best satisfies all constraints.
            If no clear answer, return 000 as default.
            Output ONLY the 3-digit integer, nothing else.""",
            context=synthesis
        )

        return final_answer