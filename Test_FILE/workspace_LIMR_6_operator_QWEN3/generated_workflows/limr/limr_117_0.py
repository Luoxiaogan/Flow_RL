# Workflow ID: limr_117_0
# Benchmark: limr
# Data Indices: [95, 90]

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

        # STEP 1: SEMANTIC DECOMPOSITION
        decomposition_instruction = """
        Break down the problem into logically independent subproblems. For each subproblem:
        - Clearly state what needs to be solved
        - Identify required mathematical domain (algebra, combinatorics, number theory, etc.)
        - Note any dependencies on other subproblems
        - Flag if the subproblem is computational (suitable for code) or symbolic (requires derivation)
        Structure output as a list of dictionaries with keys: id, description, dependencies, type (computational|symbolic).
        """
        subproblems = await self.decompose(instruction=decomposition_instruction, context="")

        # Sort subproblems by dependency (topological order)
        def resolve_dependencies(subproblems):
            resolved = []
            pending = {sp['id']: sp for sp in subproblems}
            while pending:
                for sp_id, sp in list(pending.items()):
                    deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
                    if all(dep.strip() in [r['id'] for r in resolved] for dep in deps if dep.strip()):
                        resolved.append(pending.pop(sp_id))
            return resolved

        ordered_subproblems = resolve_dependencies(subproblems)

        # STEP 2: PARALLEL SUBPROBLEM SOLVING WITH STRATEGY BRANCHING
        async def solve_subproblem(sp):
            sp_id = sp['id']
            description = sp['description']
            sp_type = sp.get('type', 'symbolic').lower()
            
            context_intro = f"Solving subproblem {sp_id}: {description}"

            if 'computational' in sp_type:
                # Programmer path with verification loop
                code_instruction = f"""
                {context_intro}
                Write Python code to solve this subproblem. Requirements:
                - Use exact arithmetic (fractions, integers, no floats unless unavoidable)
                - Include assertions to validate intermediate results
                - Return final answer in a variable named 'result'
                - If multiple solutions, return all in a list
                - Handle edge cases explicitly
                """
                solution = await self.programmer(instruction=code_instruction, context="", max_retries=3)
                
                # Verification step
                verify_instruction = f"""
                Verify the following computational solution for subproblem {sp_id}:
                {solution}
                
                Check for:
                - Correctness of logic
                - Adherence to problem constraints
                - Edge case handling
                - Numerical precision
                
                If errors found, explain them. Otherwise, output "VERIFIED".
                """
                verification = await self.generate(instruction=verify_instruction, context=solution)
                
                if "VERIFIED" not in verification:
                    # Revise and retry
                    revised_instruction = f"""
                    Fix the errors identified in verification:
                    {verification}
                    
                    Original solution attempt:
                    {solution}
                    
                    Provide corrected code or derivation.
                    """
                    solution = await self.revise(instruction=revised_instruction, context=solution)
                
                return {"id": sp_id, "solution": solution, "type": "computational"}
            
            else:
                # Symbolic path with parallel exploration
                perspectives = await asyncio.gather(
                    self.generate(instruction=f"""
                    {context_intro}
                    Solve using algebraic manipulation. Show all steps. Verify each transformation.
                    """, context=""),
                    self.generate(instruction=f"""
                    {context_intro}
                    Solve using substitution or transformation (e.g., change of variables, symmetry exploitation).
                    """, context=""),
                    self.generate(instruction=f"""
                    {context_intro}
                    Solve by assuming specific values or testing boundary cases to infer general solution.
                    """, context="")
                )
                
                # Ensemble select best symbolic solution
                ensemble_instruction = f"""
                Evaluate these three solution attempts for subproblem {sp_id}:
                1. Algebraic manipulation
                2. Transformation approach
                3. Boundary case inference
                
                Criteria:
                - Mathematical rigor
                - Completeness of steps
                - Adherence to constraints
                - Elegance and simplicity
                
                Select the best solution. If none are fully correct, synthesize a corrected version.
                """
                best_solution = await self.ensemble(instruction=ensemble_instruction, contexts_list=perspectives)
                
                # Final verification
                verify_symbolic = await self.generate(instruction=f"""
                Critically verify this symbolic solution for subproblem {sp_id}:
                {best_solution}
                
                Attempt to find counterexamples or logical gaps. If none, output "VERIFIED".
                """, context=best_solution)
                
                if "VERIFIED" not in verify_symbolic:
                    best_solution = await self.revise(instruction=f"""
                    Incorporate the following critique to fix the solution:
                    {verify_symbolic}
                    """, context=best_solution)
                
                return {"id": sp_id, "solution": best_solution, "type": "symbolic"}

        # Solve all subproblems in parallel
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in ordered_subproblems]
        )

        # STEP 3: SYNTHESIZE FINAL ANSWER
        synthesis_context = "\n\n".join([
            f"Subproblem {sol['id']} ({sol['type']}): {sol['solution']}"
            for sol in subproblem_solutions
        ])

        final_synthesis = await self.generate(instruction=f"""
        Synthesize a complete solution to the original problem using these subproblem solutions:
        {synthesis_context}
        
        Steps:
        1. Reconstruct the full solution path
        2. Ensure all constraints from original problem are satisfied
        3. Derive the final numerical answer (must be integer 000-999)
        4. Double-check arithmetic and logic
        
        Output ONLY the final integer answer in the format: ###ANSWER: XXX
        """, context=synthesis_context)

        # STEP 4: EXTRACTION AND FORMATTING
        extract_answer = await self.generate(instruction="""
        Extract the final integer answer from the following text. It should be between 000 and 999.
        If multiple numbers exist, select the one that logically answers the original problem.
        If no clear answer, return 000.
        
        Format: ###ANSWER: XXX
        """, context=final_synthesis)

        # Ensure proper formatting
        if "###ANSWER:" not in extract_answer:
            extract_answer = f"###ANSWER: {extract_answer.strip()}"
        
        # Final validation: must be 3-digit integer
        import re
        match = re.search(r'###ANSWER:\s*(\d{1,3})', extract_answer)
        if match:
            answer = int(match.group(1))
            if 0 <= answer <= 999:
                final_answer = f"{answer:03d}"  # Zero-pad to 3 digits
            else:
                final_answer = "000"
        else:
            final_answer = "000"

        return f"###ANSWER: {final_answer}"