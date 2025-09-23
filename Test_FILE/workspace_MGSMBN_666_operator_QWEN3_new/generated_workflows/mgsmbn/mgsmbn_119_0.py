# Workflow ID: mgsmbn_119_0
# Benchmark: mgsmbn
# Data Indices: [141, 121]

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

        # STEP 1: Annotate the problem - extract entities, units, actions, constraints
        annotation = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and extract structured metadata. Identify:
            1. All named entities (people, objects) and their roles
            2. All numerical values with their units and what they represent
            3. All actions or operations implied (e.g., 'ছাড়াচ্ছেন' implies subtraction of peel, 'ফেরত পেয়েছেন' implies change calculation)
            4. Temporal or logical dependencies (sequence of events)
            5. Approximations or uncertainties (e.g., 'প্রায়', 'মোটামুটি')
            6. The explicit question being asked
            Format as a JSON-like structure with clear keys. Be exhaustive.""",
            context=""
        )

        # STEP 2: Decompose into subproblems with dependencies
        subproblems = await self.decompose(
            instruction=f"""Based on the annotated structure:
            {annotation}
            
            Break down the problem into atomic, solvable subproblems. Each subproblem should:
            - Represent one mathematical or logical operation
            - Have clear inputs and expected outputs
            - Specify dependencies (which other subproblems must be solved first)
            - Preserve unit tracking throughout
            Return as a list of subproblem dictionaries with 'id', 'description', and 'dependencies'.""",
            context=annotation
        )

        # STEP 3: For each subproblem, generate multiple interpretations in parallel
        interpretation_tasks = []
        for sp in subproblems:
            # Generate 3 interpretations: exact, approximate, and contextually adjusted
            task = asyncio.gather(
                self.generate(
                    instruction=f"""Interpret subproblem EXACTLY as written:
                    {sp['description']}
                    Use precise values and literal operations. No rounding or assumptions.""",
                    context=annotation
                ),
                self.generate(
                    instruction=f"""Interpret subproblem with REAL-WORLD ADJUSTMENTS:
                    {sp['description']}
                    Consider approximations, practical constraints, and implied operations.""",
                    context=annotation
                ),
                self.generate(
                    instruction=f"""Interpret subproblem with ALTERNATIVE MATHEMATICAL MODEL:
                    {sp['description']}
                    Try algebraic, proportional, or rate-based approaches if applicable.""",
                    context=annotation
                )
            )
            interpretation_tasks.append(task)

        # Execute all interpretation tasks in parallel
        all_interpretations = await asyncio.gather(*interpretation_tasks)

        # STEP 4: For each subproblem, ensemble the best interpretation
        refined_subproblems = []
        for i, interpretations in enumerate(all_interpretations):
            best_interpretation = await self.ensemble(
                instruction=f"""Select the most contextually and mathematically appropriate interpretation for subproblem {subproblems[i]['id']}:
                - Must align with entity annotations and units
                - Must be computationally feasible
                - Must respect real-world constraints (no negative people, etc.)
                - Prefer interpretations that chain cleanly with dependencies
                Return only the selected interpretation text.""",
                contexts_list=list(interpretations)
            )
            refined_subproblems.append({
                'id': subproblems[i]['id'],
                'description': best_interpretation,
                'dependencies': subproblems[i]['dependencies']
            })

        # STEP 5: Topological sort of subproblems by dependencies
        def topological_sort(subproblems):
            # Build dependency graph
            graph = {sp['id']: sp['dependencies'].split(',') if sp['dependencies'] else [] for sp in subproblems}
            visited = set()
            sorted_order = []
            
            def visit(node):
                if node in visited:
                    return
                visited.add(node)
                for dep in graph.get(node, []):
                    if dep.strip():
                        visit(dep.strip())
                sorted_order.append(node)
            
            for sp in subproblems:
                visit(sp['id'])
            return sorted_order

        execution_order = topological_sort(refined_subproblems)
        subproblem_map = {sp['id']: sp for sp in refined_subproblems}

        # STEP 6: Execute subproblems in order, using programmer with context chaining
        results = {}
        for sp_id in execution_order:
            sp = subproblem_map[sp_id]
            # Build context from dependencies
            dep_context = "\n".join([f"Result from {dep}: {results[dep]}" for dep in sp['dependencies'].split(',') if dep.strip() in results])
            
            full_context = f"""ANNOTATION: {annotation}

DEPENDENCY RESULTS:
{dep_context}

SUBPROBLEM TO SOLVE:
{sp['description']}"""
            
            # Generate and execute code
            result = await self.programmer(
                instruction=f"""Generate and execute Python code to solve this subproblem:
                - Use exact arithmetic unless approximation is explicitly required
                - Track units throughout (convert if necessary)
                - Validate for real-world plausibility (no negatives, etc.)
                - Return ONLY the numerical result, no explanation
                Context: {full_context}""",
                context=full_context,
                max_retries=3
            )
            results[sp_id] = result

        # STEP 7: Extract final answer (last subproblem in chain)
        final_answer = results[execution_order[-1]] if execution_order else "0"

        # STEP 8: Validate and revise if needed (up to 3 iterations)
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""SANITY CHECK:
                Problem: {self.problem_text}
                Annotation: {annotation}
                Final Answer: {final_answer}
                
                Check:
                1. Does the magnitude make real-world sense? (e.g., 95 seconds for 60 potatoes? 90*60=5400s=90min, not 95s → ERROR)
                2. Are units consistent throughout?
                3. Does it satisfy all constraints from annotation?
                4. Is there any logical contradiction?
                
                If any issue found, describe it concisely. If no issues, return 'VALID'.""",
                context=f"Final Answer: {final_answer}"
            )
            
            if "VALID" in validation or "valid" in validation:
                break
            else:
                # Revise the entire approach
                final_answer = await self.revise(
                    instruction=f"""REVISE ENTIRE SOLUTION due to validation failure:
                    Validation Feedback: {validation}
                    Re-examine initial annotation and decomposition. Consider:
                    - Were units misinterpreted? (minutes vs seconds?)
                    - Was an operation missed? (addition vs multiplication?)
                    - Were dependencies incorrectly ordered?
                    Return ONLY the revised numerical answer.""",
                    context=f"Previous Answer: {final_answer}\nValidation: {validation}\nAnnotation: {annotation}"
                )

        # STEP 9: Summarize solution for transparency (optional, not returned)
        await self.summarize(
            instruction="""Create a concise, human-readable summary of the entire solution process:
            - Key entities and values extracted
            - Main steps taken
            - Why the final answer makes sense
            This is for auditing purposes, not for answer extraction.""",
            context=f"Annotation: {annotation}\nFinal Answer: {final_answer}"
        )

        return final_answer