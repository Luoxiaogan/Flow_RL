# Workflow ID: limr_38_0
# Benchmark: limr
# Data Indices: [263, 208]

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

        # PHASE 1: META-EXPLORATION — Generate multiple solution lenses
        exploration_lenses = [
            "algebraic",
            "geometric",
            "combinatorial",
            "number_theoretic",
            "probabilistic",
            "invariant-based"
        ]
        
        lens_analyses = await asyncio.gather(*[
            self.generate(
                instruction=f"""Adopt a {lens} perspective to analyze the problem:
                - What are the key variables, relationships, or structures from this viewpoint?
                - What known theorems, identities, or techniques apply?
                - What subproblems emerge naturally?
                - What assumptions or transformations simplify the problem?
                Output a structured analysis with clear section headers.""",
                context=""
            ) for lens in exploration_lenses
        ])

        # PHASE 2: DECOMPOSITION — Break each lens into executable subproblems
        decomposition_tasks = []
        for i, analysis in enumerate(lens_analyses):
            decomposition_tasks.append(
                self.decompose(
                    instruction=f"""Decompose the {exploration_lenses[i]} analysis into atomic, solvable subproblems:
                    - Each subproblem must be self-contained with clear inputs/outputs
                    - Specify dependencies (e.g., '2,3' means depends on subproblems 2 and 3)
                    - Flag any subproblem as 'high_risk: true' if it involves division, modular inverses, floating point, or unproven assumptions
                    - Include variable definitions and constraints from the analysis""",
                    context=analysis
                )
            )
        
        all_subproblem_sets = await asyncio.gather(*decomposition_tasks)

        # Flatten and index all subproblems globally
        global_subproblem_index = 0
        indexed_subproblems = []
        lens_mapping = {}

        for lens_idx, subproblem_set in enumerate(all_subproblem_sets):
            lens_name = exploration_lenses[lens_idx]
            for subproblem in subproblem_set:
                subproblem['lens'] = lens_name
                subproblem['global_id'] = f"L{lens_idx}_S{global_subproblem_index}"
                subproblem['original_id'] = subproblem['id']
                subproblem['status'] = 'pending'
                subproblem['result'] = None
                subproblem['confidence'] = 0
                indexed_subproblems.append(subproblem)
                global_subproblem_index += 1
            lens_mapping[lens_name] = [sp['global_id'] for sp in subproblem_set]

        # Build dependency graph
        dep_graph = {}
        id_to_subproblem = {sp['global_id']: sp for sp in indexed_subproblems}
        
        for sp in indexed_subproblems:
            deps = sp.get('dependencies', '').strip()
            if deps:
                dep_list = [f"L{lens_idx}_S{dep}" for dep in deps.split(',') if dep.strip()]
                dep_graph[sp['global_id']] = dep_list
            else:
                dep_graph[sp['global_id']] = []

        # PHASE 3: EXECUTION — Solve subproblems with appropriate tools, respecting dependencies
        async def solve_subproblem(subproblem, retry_count=0):
            try:
                # Determine tool based on content
                if any(kw in subproblem['description'].lower() for kw in ['compute', 'calculate', 'sum', 'product', 'mod', 'numerical']):
                    tool = 'programmer'
                else:
                    tool = 'revise'

                if tool == 'programmer':
                    code_instruction = f"""Generate Python code to solve this subproblem:
                    Description: {subproblem['description']}
                    Constraints: Use exact arithmetic. Avoid floating point. Handle edge cases.
                    If modular arithmetic is involved, use pow(base, exp, mod) for efficiency.
                    Output only the final numerical result as a Python expression.
                    Do not include print statements or explanations."""
                    
                    result = await self.programmer(
                        instruction=code_instruction,
                        context=subproblem['description'],
                        max_retries=2
                    )
                else:
                    revise_instruction = f"""Develop a rigorous, step-by-step solution to this subproblem:
                    {subproblem['description']}
                    - Justify each step with mathematical reasoning
                    - Reference relevant theorems or identities
                    - Box the final answer at the end
                    - If stuck, propose an alternative approach"""
                    
                    draft = await self.generate(instruction=revise_instruction, context="")
                    result = await self.revise(
                        instruction="Strengthen logical flow, verify calculations, and ensure conclusion follows from premises",
                        context=draft
                    )

                # Extract confidence
                confidence_check = await self.generate(
                    instruction="Rate your confidence in this solution (1-10) and briefly justify. Format: 'Confidence: X/10 - [reason]'",
                    context=result
                )
                confidence_score = 5  # default
                if "Confidence:" in confidence_check:
                    try:
                        conf_str = confidence_check.split("Confidence:")[1].split("/10")[0].strip()
                        confidence_score = int(conf_str)
                    except:
                        pass

                subproblem['result'] = result
                subproblem['confidence'] = confidence_score
                subproblem['status'] = 'solved'
                
                return result

            except Exception as e:
                if retry_count < 2:
                    # Retry with adversarial critique
                    critique = await self.generate(
                        instruction=f"Assume this solution is wrong. What is the most likely error? How would you fix it?",
                        context=subproblem.get('result', str(e))
                    )
                    fixed_instruction = f"Original attempt failed. Critique: {critique}. Revise solution addressing these flaws."
                    subproblem['result'] = await self.revise(instruction=fixed_instruction, context=subproblem.get('result', ""))
                    return await solve_subproblem(subproblem, retry_count + 1)
                else:
                    subproblem['status'] = 'failed'
                    subproblem['result'] = f"ERROR: {str(e)}"
                    return None

        # Topological sort for dependency resolution
        def topological_sort(graph):
            visited = set()
            temp = set()
            order = []
            
            def visit(node):
                if node in temp:
                    raise Exception("Circular dependency detected")
                if node in visited:
                    return
                temp.add(node)
                for dep in graph.get(node, []):
                    visit(dep)
                temp.remove(node)
                visited.add(node)
                order.append(node)
            
            for node in graph:
                if node not in visited:
                    visit(node)
            return order

        execution_order = topological_sort(dep_graph)
        
        # Execute in order
        for global_id in execution_order:
            sp = id_to_subproblem[global_id]
            if sp['status'] == 'pending':
                await solve_subproblem(sp)

        # PHASE 4: SYNTHESIS — Combine lens-specific results into final answer
        lens_results = {}
        for lens_name in exploration_lenses:
            lens_subproblems = [sp for sp in indexed_subproblems if sp['lens'] == lens_name and sp['status'] == 'solved']
            if lens_subproblems:
                # Find the "final" subproblem (likely last in decomposition or highest confidence)
                final_sp = max(lens_subproblems, key=lambda x: x['confidence'])
                lens_results[lens_name] = final_sp['result']

        if not lens_results:
            # Fallback: ensemble on raw lens analyses
            final_answer = await self.ensemble(
                instruction="""No subproblems solved successfully. Synthesize from high-level analyses.
                Extract any numerical answers mentioned. If none, propose most plausible answer based on reasoning.
                Format final answer as 3-digit string (000-999).""",
                contexts_list=lens_analyses
            )
        else:
            final_answer = await self.ensemble(
                instruction="""Synthesize solutions from multiple mathematical lenses:
                - If all lenses agree on a numerical answer, return it.
                - If they disagree, identify the point of divergence and re-analyze the conflicting assumption.
                - Prefer answers with higher confidence scores.
                - Final output must be a 3-digit integer (000-999) as string. No explanations.""",
                contexts_list=list(lens_results.values())
            )

        # PHASE 5: FINAL FORMATTING
        formatted_answer = await self.summarize(
            instruction="""Extract ONLY the final 3-digit numerical answer from the text.
            - Remove all units, explanations, and markdown.
            - If answer is less than 100, pad with leading zeros (e.g., 42 → 042).
            - If no clear answer, return '000'.
            - Output must be exactly 3 characters.""",
            context=final_answer
        )

        return formatted_answer.strip()[:3].zfill(3)