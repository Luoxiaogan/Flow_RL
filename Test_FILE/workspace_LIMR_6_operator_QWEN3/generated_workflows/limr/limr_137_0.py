# Workflow ID: limr_137_0
# Benchmark: limr
# Data Indices: [256, 21]

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

        # PHASE 1: STRATEGIC EXPLORATION — Generate multiple solution hypotheses in parallel
        exploration_strategies = [
            "Approach this as an optimization problem using inequalities (AM-GM, Cauchy-Schwarz, Power Mean, etc.). Identify variables, constraints, and objective. Propose a bounding strategy.",
            "Approach this as an algebraic manipulation problem. Look for substitutions, symmetries, or invariant transformations. Propose variable reductions or normalization steps.",
            "Approach this as a combinatorial or number-theoretic problem. Consider integer constraints, modular arithmetic, or counting arguments. Propose case analysis or constructive examples.",
            "Approach this computationally: identify what could be simulated, enumerated, or calculated numerically. Propose a brute-force or search-based strategy with bounds."
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{instr}

                Analyze the original problem and outline a detailed solution strategy in 5 steps or fewer. 
                For each step, state: what mathematical tool is used, what sub-result is expected, and what risk or assumption is involved.
                Do NOT compute the final answer yet — focus on strategy viability and structure.
                """,
                context=""
            ) for instr in exploration_strategies]
        )

        # Rank and synthesize strategies
        synthesized_strategy = await self.ensemble(
            instruction="""Evaluate the proposed strategies and select the most promising one or synthesize a hybrid approach. Criteria:
            - Mathematical elegance and minimality of assumptions
            - Computational tractability (avoid exponential complexity unless bounded)
            - Alignment with problem constraints and answer format (integer 000-999)
            - Presence of verifiable intermediate steps

            Output a single unified strategy description, clearly numbered in steps, incorporating the best elements from the candidates.
            """,
            contexts_list=strategy_attempts
        )

        # PHASE 2: STRUCTURED EXECUTION — Decompose and execute the chosen strategy
        decomposition = await self.decompose(
            instruction="""Break down the selected strategy into atomic, executable subproblems. For each:
            - Define precise mathematical task (e.g., 'Prove inequality X >= Y', 'Solve equation Z for integer k')
            - List dependencies (which subproblems must be solved first)
            - Specify whether it is analytical (proof-based) or computational (requires calculation)

            Prioritize subproblems that can be parallelized or validated independently.
            """,
            context=synthesized_strategy
        )

        # Execute subproblems in topological order, parallelizing independent ones
        subproblem_results = {}
        # Group subproblems by dependency level (simple topological sort)
        dependency_graph = {sp['id']: sp['dependencies'].split(',') if sp['dependencies'] else [] for sp in decomposition}
        all_ids = [sp['id'] for sp in decomposition]
        solved_ids = set()

        while len(solved_ids) < len(all_ids):
            # Find subproblems with all dependencies resolved
            ready = [sp for sp in decomposition if sp['id'] not in solved_ids and all(dep in solved_ids for dep in dependency_graph[sp['id']])]
            
            if not ready:
                # Circular dependency or missing step — break with error
                break

            # Execute ready subproblems in parallel
            tasks = []
            for sp in ready:
                if "compute" in sp['description'].lower() or "calculate" in sp['description'].lower() or "enumerate" in sp['description'].lower():
                    # Computational subproblem
                    task = self.programmer(
                        instruction=f"""Implement and execute a solution for: {sp['description']}
                        Use exact arithmetic. If brute force, bound the search space intelligently.
                        Return only the final result in a code comment at the end, like: # RESULT: 123
                        """,
                        context=json.dumps(subproblem_results)
                    )
                else:
                    # Analytical subproblem
                    task = self.generate(
                        instruction=f"""Solve this mathematical subproblem rigorously: {sp['description']}
                        Show all steps. Justify key insights. Box the final sub-result.
                        If stuck, state why and propose an alternative approach.
                        """,
                        context=json.dumps(subproblem_results)
                    )
                tasks.append((sp['id'], task))

            # Run tasks in parallel
            results = await asyncio.gather(*[t[1] for t in tasks])
            for i, sp_id in enumerate([t[0] for t in tasks]):
                subproblem_results[sp_id] = results[i]
                solved_ids.add(sp_id)

        # PHASE 3: VALIDATION & SYNTHESIS — Cross-verify and refine
        # Attempt independent verification via Programmer if not already used
        verification_task = None
        if not any("programmer" in str(v).lower() for v in subproblem_results.values()):
            verification_task = self.programmer(
                instruction="""Based on the final answer derived, write a program to verify it.
                For example: if the answer is n=125, verify by constructing an example with n=125 that satisfies the constraints, or by checking the bound is tight.
                If direct verification is impossible, compute a related quantity that indirectly confirms correctness.
                """,
                context=json.dumps(subproblem_results)
            )

        # Generate final answer extraction
        answer_draft = await self.generate(
            instruction="""From the subproblem results and synthesis, extract the final answer.
            The answer must be an integer between 000 and 999.
            State it clearly in the format: \\boxed{123}
            If multiple answers are possible, state the one that satisfies all constraints and is minimal/maximal as required.
            """,
            context=json.dumps(subproblem_results)
        )

        # Run verification in parallel with answer extraction if applicable
        if verification_task:
            verification_result, answer_refined = await asyncio.gather(
                verification_task,
                self.revise(
                    instruction="Improve clarity and ensure answer format is \\boxed{XXX}. Verify against subproblem logic.",
                    context=answer_draft
                )
            )
            # Use verification to revise if discrepancy
            final_answer = await self.ensemble(
                instruction="""Reconcile the analytical answer and computational verification.
                If they agree, output the answer.
                If they disagree, identify the error in reasoning or code, and correct the answer.
                Final output must be a single integer in \\boxed{} format.
                """,
                contexts_list=[answer_refined, verification_result]
            )
        else:
            final_answer = await self.revise(
                instruction="""Final sanity check: 
                - Is the answer an integer between 000 and 999?
                - Does it logically follow from the subproblems?
                - Are all constraints satisfied?
                If any doubt, re-derive the critical step.
                Output only the final answer in \\boxed{XXX} format.
                """,
                context=answer_draft
            )

        return final_answer