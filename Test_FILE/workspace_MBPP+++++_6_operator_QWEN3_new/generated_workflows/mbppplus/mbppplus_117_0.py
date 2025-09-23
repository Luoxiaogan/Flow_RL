# Workflow ID: mbppplus_117_0
# Benchmark: mbppplus
# Data Indices: [238, 339]

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

        # Step 1: Decompose the problem into subproblems with dependencies
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into atomic, testable subproblems.
            For each subproblem:
            - Describe what needs to be implemented or decided
            - Specify if it's a helper function, main logic, edge case handler, or type converter
            - List dependencies (other subproblems that must be solved first)
            - Note any constraints (time complexity, return type, mutability, etc.)
            Focus on: core algorithm, edge cases (empty/single/mixed inputs), type handling, and helper functions.
            Format each as {'id': 'step_X', 'description': '...', 'dependencies': 'step_Y,step_Z'}""",
            context=""
        )

        # Step 2: Group subproblems by dependency level (topological sort)
        subproblems_by_level = {}
        subproblem_map = {sp['id']: sp for sp in decomposition}
        remaining = set(subproblem_map.keys())
        
        level = 0
        while remaining:
            # Find subproblems with all dependencies resolved
            current_level = [
                sp_id for sp_id in remaining 
                if all(dep.strip() in subproblem_map and dep.strip() not in remaining 
                      for dep in subproblem_map[sp_id]['dependencies'].split(',') if dep.strip())
            ]
            if not current_level:
                break  # Circular dependency or error
            subproblems_by_level[level] = current_level
            remaining -= set(current_level)
            level += 1

        # Step 3: Process each level in parallel
        solutions = {}
        for level_idx in sorted(subproblems_by_level.keys()):
            level_subproblems = subproblems_by_level[level_idx]
            
            # Generate initial solutions for this level in parallel
            generate_tasks = []
            for sp_id in level_subproblems:
                sp = subproblem_map[sp_id]
                deps_context = "\n".join([
                    f"Dependency {dep}: {solutions.get(dep, 'Not implemented yet')}"
                    for dep in sp['dependencies'].split(',') if dep.strip()
                ])
                
                task = self.generate(
                    instruction=f"""Solve this subproblem:
                    {sp['description']}
                    
                    Context from dependencies:
                    {deps_context}
                    
                    Constraints:
                    - Match exact function signatures and return types
                    - Handle edge cases: empty inputs, single elements, type mismatches
                    - Prefer clarity and correctness over premature optimization
                    - If implementing a helper, ensure it's reusable and well-named
                    - Return ONLY the code snippet for this subproblem, no explanations""",
                    context=deps_context
                )
                generate_tasks.append(task)
            
            level_solutions = await asyncio.gather(*generate_tasks)
            
            # Revise each solution for robustness
            revise_tasks = []
            for i, sp_id in enumerate(level_subproblems):
                sp = subproblem_map[sp_id]
                solution = level_solutions[i]
                
                revise_task = self.revise(
                    instruction=f"""Improve this solution:
                    {solution}
                    
                    Requirements:
                    - Verify edge case handling (empty, single, duplicates, mixed types)
                    - Ensure type consistency (input/output types match problem)
                    - Check for off-by-one errors, boundary conditions
                    - Optimize only if complexity is worse than standard for this problem
                    - Preserve order if required by problem
                    - Return ONLY the revised code snippet, no markdown or explanations""",
                    context=solution
                )
                revise_tasks.append(revise_task)
            
            revised_solutions = await asyncio.gather(*revise_tasks)
            
            # Store solutions
            for i, sp_id in enumerate(level_subproblems):
                solutions[sp_id] = revised_solutions[i]

        # Step 4: Synthesize full solution from components
        all_solutions_text = "\n\n".join([
            f"Subproblem {sp_id}: {solutions[sp_id]}"
            for sp_id in subproblem_map.keys()
        ])
        
        synthesized = await self.ensemble(
            instruction=f"""Synthesize a complete, runnable solution from these components:
            {all_solutions_text}
            
            Requirements:
            - Integrate helper functions and main logic coherently
            - Ensure function names and signatures match the problem exactly
            - Handle all edge cases identified in decomposition
            - Return ONLY the complete code with all necessary functions, no explanations
            - Include imports if needed
            - Preserve the exact function name and parameter names from the problem""",
            contexts_list=[all_solutions_text]
        )

        # Step 5: Validate and iterate if needed
        validation = await self.generate(
            instruction=f"""Critique this solution for robustness:
            {synthesized}
            
            Check:
            - Does it handle empty inputs?
            - Does it handle single-element inputs?
            - Are return types correct (list vs tuple vs set)?
            - Are there any type assumptions that could break with mixed inputs?
            - Is the algorithm correct for all test cases?
            - Are helper functions properly integrated?
            
            If any issues, describe them concisely. If perfect, say 'VALID'.""",
            context=synthesized
        )

        final_code = synthesized
        if "VALID" not in validation.upper():
            # One revision pass
            final_code = await self.revise(
                instruction=f"""Fix these issues:
                {validation}
                
                Original solution:
                {synthesized}
                
                Requirements:
                - Address all critique points
                - Maintain all previous functionality
                - Return ONLY the corrected code, no explanations""",
                context=synthesized
            )

        # Extract just the code block if it's wrapped in markdown
        code_match = re.search(r'