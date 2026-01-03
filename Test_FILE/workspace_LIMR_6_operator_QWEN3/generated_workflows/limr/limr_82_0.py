# Workflow ID: limr_82_0
# Benchmark: limr
# Data Indices: [193, 41]

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

        # Step 1: Generate multiple problem interpretations in parallel
        perspectives = await asyncio.gather(
            self.generate(
                instruction="""Analyze this problem from a geometric perspective. Identify shapes, coordinates, distances, or spatial relationships. Suggest how geometric principles or coordinate systems could be applied. Ignore non-geometric aspects.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from an algebraic/number-theoretic perspective. Identify equations, variables, polynomials, roots, or number properties. Suggest algebraic manipulations, substitutions, or theorem applications. Ignore geometric or combinatorial aspects.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a combinatorial/probabilistic perspective. Identify counting principles, permutations, probabilities, or discrete structures. Suggest combinatorial arguments or probabilistic methods. Ignore continuous or geometric aspects.""",
                context=""
            )
        )

        # Step 2: Synthesize perspectives into unified problem understanding
        unified_analysis = await self.ensemble(
            instruction="""Synthesize the three perspectives into a single coherent problem analysis. Identify the dominant mathematical domain, but preserve cross-domain insights. Highlight key variables, constraints, and what needs to be solved. Format as: 'Domain: [primary domain]. Key elements: [list]. Solution approach: [brief strategy].'""",
            contexts_list=perspectives
        )

        # Step 3: Generate two parallel decomposition strategies
        decomposition_strategies = await asyncio.gather(
            self.decompose(
                instruction="""Decompose the problem using a formal mathematical approach: break into equations, constraints, and unknowns. Each subproblem should represent a solvable mathematical unit (e.g., 'solve for x', 'minimize expression').""",
                context=unified_analysis
            ),
            self.decompose(
                instruction="""Decompose the problem using an intuitive reasoning approach: break into conceptual steps a human mathematician might take (e.g., 'first, visualize the setup', 'then, apply symmetry'). Focus on logical flow over formalism.""",
                context=unified_analysis
            )
        )

        # Step 4: Ensemble decompositions into final task graph
        # Convert decompositions to string representations for ensembling
        decomposition_strings = [
            "\n".join([f"ID: {sp['id']}, Desc: {sp['description']}, Deps: {sp['dependencies']}" for sp in decomposition_strategies[0]]),
            "\n".join([f"ID: {sp['id']}, Desc: {sp['description']}, Deps: {sp['dependencies']}" for sp in decomposition_strategies[1]])
        ]

        final_decomposition_str = await self.ensemble(
            instruction="""Merge the two decompositions into a single, robust task graph. Resolve conflicts by preferring formal mathematical subproblems when available, but retain intuitive steps if they provide critical insight. Output as a numbered list of subproblems with dependencies in format: '1. [description] (depends on: [ids])'. Ensure no cyclic dependencies.""",
            contexts_list=decomposition_strings
        )

        # Parse final decomposition back into structured format
        subproblems = []
        for line in final_decomposition_str.split('\n'):
            if not line.strip():
                continue
            # Extract ID, description, and dependencies
            match = re.match(r'^(\d+)\.\s*(.*?)\s*\(depends on:\s*(.*?)\)$', line.strip())
            if match:
                sp_id = f"sp_{match.group(1)}"
                desc = match.group(2)
                deps = match.group(3).strip()
                dep_list = [f"sp_{x.strip()}" for x in deps.split(',')] if deps and deps.lower() != 'none' else []
                subproblems.append({
                    'id': sp_id,
                    'description': desc,
                    'dependencies': ','.join(dep_list) if dep_list else ""
                })

        # Step 5: Solve subproblems with appropriate tools (conditional routing)
        subproblem_solutions = {}
        subproblem_order = self._topological_sort(subproblems)

        for sp in subproblem_order:
            # Determine solution approach for this subproblem
            approach_analysis = await self.generate(
                instruction=f"""For subproblem: '{sp['description']}', recommend the best solution approach. Choose from:
                - PROGRAMMING: if it requires precise calculation, equation solving, or algorithmic steps.
                - MATHEMATICAL_DERIVATION: if it requires proof, algebraic manipulation, or theoretical reasoning.
                Justify your choice in one sentence. Format: 'APPROACH: [PROGRAMMING|MATHEMATICAL_DERIVATION]. REASON: [justification]'""",
                context=unified_analysis
            )

            # Extract approach
            approach = "PROGRAMMING" if "PROGRAMMING" in approach_analysis else "MATHEMATICAL_DERIVATION"

            # Build context from dependencies
            dep_context = "\n".join([f"Subproblem {dep}: {subproblem_solutions.get(dep, 'Not solved yet')}" 
                                   for dep in sp['dependencies'].split(',') if dep])

            if approach == "PROGRAMMING":
                # Use programmer for computational subproblems
                raw_solution = await self.programmer(
                    instruction=f"""Solve this subproblem precisely: '{sp['description']}'. 
                    Context from dependencies: {dep_context}
                    Generate Python code that computes the answer. Handle edge cases. Output only the final result as a number or simple expression.""",
                    context=dep_context
                )
            else:
                # Use generate + revise for theoretical subproblems
                raw_solution = await self.generate(
                    instruction=f"""Solve this subproblem through mathematical reasoning: '{sp['description']}'. 
                    Context from dependencies: {dep_context}
                    Show all steps. Use theorems or identities as needed. Box the final answer.""",
                    context=dep_context
                )
                # Revise for rigor
                raw_solution = await self.revise(
                    instruction="""Critique this solution for logical gaps, algebraic errors, or unjustified assumptions. 
                    Verify each step. If any flaw is found, correct it. Ensure the final answer is clearly stated and matches the subproblem requirements.""",
                    context=raw_solution
                )

            # Store solution
            subproblem_solutions[sp['id']] = raw_solution

        # Step 6: Integrate solutions and validate globally
        integrated_solution = "\n\n".join([f"Subproblem {sp['id']}: {sp['description']} => {subproblem_solutions[sp['id']]}" 
                                         for sp in subproblems])

        global_validation = await self.generate(
            instruction=f"""Given the integrated solution: {integrated_solution}
            Verify that it satisfies ALL original problem constraints and requirements. 
            Check for consistency, unit compatibility, and logical coherence. 
            If any issue is found, identify which subproblem(s) are likely responsible and suggest corrections. 
            If no issues, state 'VALIDATED: Solution is consistent and complete.'""",
            context=integrated_solution
        )

        # Step 7: If validation fails, attempt targeted revision
        if "issue" in global_validation.lower() or "error" in global_validation.lower():
            # Extract problematic subproblems
            revision_targets = await self.generate(
                instruction=f"""From the validation feedback: {global_validation}
                Identify exactly which subproblem IDs need revision. List them as comma-separated IDs (e.g., 'sp_1,sp_3').""",
                context=global_validation
            )
            
            target_ids = [tid.strip() for tid in revision_targets.split(',') if tid.strip().startswith('sp_')]
            
            for tid in target_ids:
                if tid in subproblem_solutions:
                    # Revise with validation feedback as context
                    revised_solution = await self.revise(
                        instruction=f"""Revise this subproblem solution based on global validation feedback: {global_validation}
                        Ensure the solution now satisfies all constraints. Show corrected steps if needed.""",
                        context=subproblem_solutions[tid]
                    )
                    subproblem_solutions[tid] = revised_solution

            # Re-integrate
            integrated_solution = "\n\n".join([f"Subproblem {sp['id']}: {sp['description']} => {subproblem_solutions[sp['id']]}" 
                                             for sp in subproblems])

        # Step 8: Extract final answer in parallel (ensemble for robustness)
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""From the final integrated solution: {integrated_solution}
                Extract the final numerical answer. It must be an integer between 000 and 999. 
                If multiple answers exist, choose the one that best satisfies the original problem. 
                Format: 'The answer is: [number]'""",
                context=integrated_solution
            ),
            self.generate(
                instruction=f"""From the final integrated solution: {integrated_solution}
                Extract the final numerical answer independently. Think step by step. 
                Format: 'The answer is: [number]'""",
                context=integrated_solution
            ),
            self.generate(
                instruction=f"""From the final integrated solution: {integrated_solution}
                Extract the final numerical answer using a different reasoning path. 
                Format: 'The answer is: [number]'""",
                context=integrated_solution
            )
        )

        # Ensemble final answers
        final_answer = await self.ensemble(
            instruction="""Select the most reliable final answer from the candidates. 
            If all agree, return that answer. If they disagree, choose the one best supported by the integrated solution. 
            Output ONLY the three-digit number (e.g., '123'), no text.""",
            contexts_list=answer_candidates
        )

        # Clean and return final answer
        # Extract just the number using regex
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            answer_num = int(match.group(1))
            # Ensure three-digit format
            return f"{answer_num:03d}"
        else:
            # Fallback: return first three digits found or 000
            digits = re.findall(r'\d', final_answer)
            if len(digits) >= 3:
                return ''.join(digits[:3])
            else:
                return "000"

    def _topological_sort(self, subproblems):
        """Sort subproblems by dependencies (topological sort)"""
        # Build dependency graph
        graph = {sp['id']: [] for sp in subproblems}
        in_degree = {sp['id']: 0 for sp in subproblems}
        
        for sp in subproblems:
            deps = sp['dependencies'].split(',') if sp['dependencies'] else []
            for dep in deps:
                if dep.strip():
                    graph[dep.strip()].append(sp['id'])
                    in_degree[sp['id']] += 1
        
        # Kahn's algorithm
        queue = [sp_id for sp_id in in_degree if in_degree[sp_id] == 0]
        result = []
        sp_map = {sp['id']: sp for sp in subproblems}
        
        while queue:
            current = queue.pop(0)
            result.append(sp_map[current])
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result