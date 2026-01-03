# Workflow ID: limr_64_0
# Benchmark: limr
# Data Indices: [132, 180]

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

        # PHASE 1: PROBLEM CLASSIFICATION & CONSTRAINT EXTRACTION
        classification = await self.generate(
            instruction="""Perform deep problem classification and constraint extraction:
            1. Identify primary domain (algebra, geometry, combinatorics, number theory, etc.)
            2. List all explicit constraints (e.g., integer answers, range limits, positivity)
            3. Infer implicit constraints (e.g., distinct values, non-degenerate shapes, valid bases)
            4. Determine solution type: exact integer, count, probability, etc.
            5. Estimate complexity level (low/medium/high) based on required steps and insights
            6. Suggest 2-3 potential solution strategies with brief rationale for each
            Format as JSON with keys: domain, explicit_constraints, implicit_constraints, solution_type, complexity, strategies""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY DEPLOYMENT
        # Launch three independent solver agents with different approaches
        agent_tasks = [
            self.generate(
                instruction=f"""Act as ALGEBRAIC/STRUCTURAL SOLVER:
                Problem classification: {classification}
                Strategy: Focus on symbolic manipulation, equation systems, invariants, and transformations.
                - Derive governing equations or relationships
                - Apply symmetry, substitution, or algebraic identities
                - Track variable dependencies and constraints
                - Output must include step-by-step derivation ending with boxed answer
                If stuck, state why and suggest alternative approach.""",
                context=""
            ),
            self.generate(
                instruction=f"""Act as COMPUTATIONAL/ENUMERATIVE SOLVER:
                Problem classification: {classification}
                Strategy: Identify bounded search space and use algorithmic enumeration.
                - Define feasible range for unknowns (use constraints from classification)
                - Design efficient search or simulation (avoid brute-force if possible)
                - Consider edge cases and boundary conditions
                - Output must include pseudocode or algorithm description + result
                If computationally infeasible, explain why and suggest symbolic approach.""",
                context=""
            ),
            self.generate(
                instruction=f"""Act as GEOMETRIC/VISUAL SOLVER:
                Problem classification: {classification}
                Strategy: Even for non-geometry problems, visualize as spatial/configurational.
                - Map elements to geometric entities (points, graphs, regions)
                - Look for spatial symmetries, invariants, or transformations
                - Use coordinate systems or vector representations if applicable
                - Output must include visual analogy + derived answer
                If no geometric interpretation, state so and pivot to combinatorial view.""",
                context=""
            )
        ]
        
        agent_results = await asyncio.gather(*agent_tasks)

        # PHASE 3: DECOMPOSITION-BASED VALIDATION
        decomposition = await self.decompose(
            instruction="""Decompose problem into subproblems based on invariants and dependencies:
            - Each subproblem should represent a necessary condition or invariant
            - Dependencies should reflect logical derivation order
            - Include at least one 'sanity check' subproblem (e.g., 'Verify answer satisfies original constraints')
            - Maximum 5 subproblems for focus
            Format each as: id, description, dependencies""",
            context=f"Classification: {classification}\nAgent Results: {' | '.join(agent_results[:200])}..."
        )

        # Solve each subproblem independently
        subproblem_solutions = {}
        for sub in decomposition:
            sub_id = sub['id']
            sub_desc = sub['description']
            deps = sub.get('dependencies', '').split(',') if sub.get('dependencies') else []
            
            # Wait for dependencies if any
            dep_context = "\n".join([f"Subproblem {d}: {subproblem_solutions.get(d, 'Not solved yet')}" for d in deps if d in subproblem_solutions]) if deps else ""
            
            solution = await self.generate(
                instruction=f"""Solve subproblem: {sub_desc}
                Context from dependencies: {dep_context}
                Classification context: {classification}
                Requirements:
                - Show complete derivation
                - Cross-verify with original problem constraints
                - If dependent on unsolved subproblems, state assumptions clearly
                - Final output must be self-contained and verifiable""",
                context=dep_context
            )
            subproblem_solutions[sub_id] = solution

        # PHASE 4: ENSEMBLE SYNTHESIS WITH PROGRAMMATIC VERIFICATION
        synthesis_contexts = [
            f"AGENT 1 (Algebraic): {agent_results[0]}",
            f"AGENT 2 (Computational): {agent_results[1]}",
            f"AGENT 3 (Geometric): {agent_results[2]}",
            f"DECOMPOSITION VERIFICATION: {' | '.join([f'{k}: {v[:100]}...' for k,v in subproblem_solutions.items()])}"
        ]

        synthesized = await self.ensemble(
            instruction="""Synthesize final answer through critical reconciliation:
            1. Compare all agent results and subproblem solutions
            2. Identify consensus answers and conflicting ones
            3. For conflicts, determine which approach violated constraints or made invalid assumptions
            4. If no consensus, design a computational verification script to test top candidates
            5. Final answer must be integer 000-999 with complete justification
            6. Include 'confidence score' (high/medium/low) based on consistency across methods
            Format: 
            - Consensus: [answer] 
            - Justification: [step-by-step reconciliation]
            - Confidence: [score]
            - Verification Plan: [if needed]""",
            contexts_list=synthesis_contexts
        )

        # PHASE 5: PROGRAMMATIC VERIFICATION (if confidence is medium/low or verification plan exists)
        final_answer = synthesized
        if "medium" in synthesized.lower() or "low" in synthesized.lower() or "verification plan" in synthesized.lower():
            verification_code = await self.generate(
                instruction=f"""Generate Python code to verify the proposed answer:
                Context: {synthesized}
                Classification: {classification}
                Requirements:
                - Code must be self-contained and executable
                - Test all constraints from original problem
                - If answer is a count, verify by enumeration or combinatorial formula
                - If answer is a value, verify by plugging back into original equations
                - Output 'VERIFIED: [answer]' if correct, 'FAILED: [reason]' if not""",
                context=synthesized
            )
            
            verification_result = await self.programmer(
                instruction="Execute verification code and return result",
                context=verification_code
            )
            
            # If verification fails, trigger revision loop
            if "FAILED" in verification_result:
                final_answer = await self.revise(
                    instruction=f"""Revise solution based on verification failure:
                    Original synthesis: {synthesized}
                    Verification result: {verification_result}
                    Requirements:
                    - Identify exact point of failure
                    - Re-derive solution with corrected assumptions
                    - Cross-validate with at least two independent methods
                    - Output final answer in boxed format""",
                    context=synthesized
                )
            else:
                final_answer = verification_result

        # PHASE 6: FINAL SANITY CHECK & FORMATTING
        final_output = await self.revise(
            instruction="""Perform final sanity check and format for submission:
            1. Confirm answer is integer between 000-999
            2. Verify all problem constraints are satisfied
            3. Ensure no step assumes unstated conditions
            4. Format as: \boxed{XXX} where XXX is 3-digit integer (pad with leading zeros if needed)
            5. If answer is single or double digit, pad to 3 digits (e.g., 5 → 005)
            Return ONLY the boxed answer, nothing else.""",
            context=final_answer
        )

        return final_output