# Workflow ID: limr_46_0
# Benchmark: limr
# Data Indices: [14, 68]

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
        
        # PHASE 1: MULTI-PERSPECTIVE DECOMPOSITION
        decomposition_instructions = [
            """Decompose this problem through an ALGEBRAIC lens:
            - Identify all variables, equations, and functional relationships
            - Break into subproblems that isolate unknowns or simplify expressions
            - Prioritize symbolic manipulation and equation solving
            - Output dependency graph of algebraic steps""",
            
            """Decompose this problem through a GEOMETRIC/SPATIAL lens:
            - Identify all spatial relationships, coordinates, or transformations
            - Break into subproblems involving distances, angles, or coordinate systems
            - Prioritize visualization and vector/matrix operations
            - Output dependency graph of geometric steps""",
            
            """Decompose this problem through a COMBINATORIAL/LOGICAL lens:
            - Identify counting principles, probability spaces, or logical constraints
            - Break into subproblems involving cases, permutations, or recursive structures
            - Prioritize enumeration and case analysis
            - Output dependency graph of combinatorial steps"""
        ]
        
        # Generate three parallel decompositions
        decompositions = await asyncio.gather(
            *[self.decompose(instr, "") for instr in decomposition_instructions]
        )
        
        # PHASE 2: SYNTHESIZE SUPER-DECOMPOSITION
        synthesis_instruction = """Synthesize these three decompositions into a unified dependency graph:
        - Preserve all unique subproblems from each perspective
        - Merge overlapping subproblems (same mathematical goal)
        - Resolve conflicts by prioritizing more computationally explicit approaches
        - Order subproblems by dependency depth (prerequisites first)
        - Output as list of subproblems with 'id', 'description', 'dependencies'"""
        
        unified_decomposition = await self.ensemble(synthesis_instruction, [str(d) for d in decompositions])
        
        # Parse the unified decomposition (assuming it returns structured text we can split)
        # In practice, this would be more robust with JSON parsing, but we'll simulate
        subproblems_raw = await self.generate(
            """Convert the unified decomposition into a Python-parseable list of dicts.
            Each dict must have keys: 'id', 'description', 'dependencies' (comma-separated string).
            Format exactly as: [{'id': '1', 'description': '...', 'dependencies': ''}, ...]""",
            context=unified_decomposition
        )
        
        # Safely evaluate the string representation of list of dicts
        try:
            import ast
            subproblems = ast.literal_eval(subproblems_raw)
        except:
            # Fallback: create minimal decomposition if parsing fails
            subproblems = await self.decompose(
                "Create a minimal viable decomposition with at most 3 essential subproblems",
                ""
            )
            # Convert to expected format if needed
            if isinstance(subproblems, list) and len(subproblems) > 0 and isinstance(subproblems[0], dict):
                pass  # already in correct format
            else:
                subproblems = [{'id': '1', 'description': 'Solve the entire problem in one step', 'dependencies': ''}]
        
        # PHASE 3: SOLVE SUBPROBLEMS WITH VERIFICATION
        solved_subproblems = {}
        verification_log = []
        
        # Topological sort by dependencies (simplified)
        unsolved = {sp['id']: sp for sp in subproblems}
        solved_ids = set()
        
        max_iterations = len(subproblems) * 3  # Prevent infinite loops
        iteration = 0
        
        while unsolved and iteration < max_iterations:
            iteration += 1
            solvable = []
            
            # Find subproblems whose dependencies are satisfied
            for sp_id, sp in unsolved.items():
                deps = [d.strip() for d in sp['dependencies'].split(',') if d.strip()]
                if all(dep in solved_ids for dep in deps):
                    solvable.append(sp)
            
            if not solvable:
                break  # Circular dependency or missing prerequisites
            
            # Solve solvable subproblems in parallel
            async def solve_subproblem(sp):
                # Generate initial solution
                solution = await self.generate(
                    f"""Solve this subproblem: {sp['description']}
                    Context from solved subproblems: {solved_subproblems}
                    Show all steps. If calculation needed, use exact arithmetic.
                    If stuck, state 'REQUIRES PROGRAMMER' and describe computation needed.""",
                    context=""
                )
                
                # Check if programmer is needed
                if "REQUIRES PROGRAMMER" in solution:
                    prog_instruction = f"""Write Python code to solve: {sp['description']}
                    Use exact arithmetic (fractions, sympy). Avoid floats.
                    Context: {solved_subproblems}"""
                    solution = await self.programmer(prog_instruction, "", max_retries=3)
                
                # Revise for verification
                verified = await self.revise(
                    f"""Critically verify this solution:
                    - Check units and dimensions
                    - Validate against edge cases
                    - Confirm no arithmetic errors
                    - Ensure consistency with prerequisite subproblems: {deps}
                    If verified, append 'VERIFIED:' prefix. If not, fix errors.""",
                    context=solution
                )
                
                return sp['id'], verified
            
            # Solve all currently solvable subproblems
            results = await asyncio.gather(*[solve_subproblem(sp) for sp in solvable])
            
            # Update solved subproblems
            for sp_id, solution in results:
                solved_subproblems[sp_id] = solution
                solved_ids.add(sp_id)
                del unsolved[sp_id]
            
            # Verification checkpoint every 2 subproblems
            if len(solved_ids) % 2 == 0 and solved_subproblems:
                checkpoint = await self.generate(
                    f"""Act as skeptical reviewer. For each solved subproblem:
                    {list(solved_subproblems.items())}
                    Attempt to find inconsistencies or errors. If none, state 'CHECKPOINT VERIFIED'.""",
                    context=""
                )
                verification_log.append(checkpoint)
                if "CHECKPOINT VERIFIED" not in checkpoint:
                    # Trigger revision of most recent subproblem
                    last_id = list(solved_subproblems.keys())[-1]
                    revised = await self.revise(
                        "Fix errors identified in verification checkpoint",
                        context=solved_subproblems[last_id]
                    )
                    solved_subproblems[last_id] = revised
        
        # PHASE 4: LATERAL THINKING & ALTERNATIVE APPROACHES
        lateral_thinking = await self.generate(
            """Assume the current solution path is fundamentally flawed.
            Generate 3 radically different approaches using:
            1. Advanced mathematical identities or theorems not yet considered
            2. Transformations to different problem domains (e.g., algebra to geometry)
            3. Exploiting hidden symmetries or invariants
            For each, outline key insight and potential solution path.""",
            context=str(solved_subproblems)
        )
        
        # PHASE 5: FINAL SYNTHESIS & ANSWER EXTRACTION
        final_synthesis = await self.ensemble(
            """Assemble final answer from all available information:
            - Primary solution path: {solved_subproblems}
            - Alternative approaches: {lateral_thinking}
            - Verification logs: {verification_log}
            
            Cross-validate all intermediate results. Resolve conflicts by:
            1. Prioritizing Programmer-generated results
            2. Then prioritizing solutions with explicit 'VERIFIED' tag
            3. Finally, selecting most mathematically rigorous approach
            
            Output must be a single integer between 000 and 999.
            If multiple valid answers, choose smallest.
            If no consistent solution, output 000.
            
            Format: exactly three digits (e.g., 007 for 7).""",
            contexts_list=[str(solved_subproblems), lateral_thinking, str(verification_log)]
        )
        
        # Final formatting and validation
        final_answer = await self.revise(
            """Ensure answer is exactly three digits (000-999):
            - Extract only the integer answer
            - Zero-pad to three digits (e.g., 7 becomes 007)
            - Remove any units, explanations, or text
            - If not a valid integer in range, output 000""",
            context=final_synthesis
        )
        
        # Extract just the three-digit number using regex as final safeguard
        match = re.search(r'\b(\d{3})\b', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any number and format
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                num = int(numbers[0]) % 1000  # Ensure in range
                return f"{num:03d}"
            else:
                return "000"