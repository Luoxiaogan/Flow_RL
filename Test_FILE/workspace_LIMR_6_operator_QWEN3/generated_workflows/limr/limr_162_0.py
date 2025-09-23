# Workflow ID: limr_162_0
# Benchmark: limr
# Data Indices: [150, 125]

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

        # STEP 1: Generate multiple problem decompositions in parallel
        decomposition_instructions = [
            """Decompose this problem with emphasis on ALGEBRAIC STRUCTURE:
            - Identify all variables, equations, and functional relationships
            - Break into subproblems that isolate equation solving, substitution, or transformation
            - Flag any polynomial, exponential, or logarithmic components
            - Dependencies should reflect algebraic derivation order""",
            
            """Decompose this problem with emphasis on COMBINATORIAL/PROBABILISTIC STRUCTURE:
            - Identify counting principles, sample spaces, events, or probability distributions
            - Break into subproblems: define universe, define favorable cases, handle constraints
            - Flag overcounting risks, independence assumptions, or symmetry exploitations
            - Dependencies should reflect logical counting order""",
            
            """Decompose this problem with emphasis on GEOMETRIC/SPATIAL STRUCTURE:
            - Identify shapes, angles, lengths, coordinates, or transformations
            - Break into subproblems: apply theorems, set up coordinate systems, compute distances/areas
            - Flag trigonometric identities, similarity, or congruence applications
            - Dependencies should reflect geometric derivation order"""
        ]

        decomposition_attempts = await asyncio.gather(
            *[self.decompose(instr, "") for instr in decomposition_instructions]
        )

        # STEP 2: Ensemble to select or synthesize best decomposition
        chosen_decomposition = await self.ensemble(
            instruction="""Select the most mathematically sound and complete decomposition path.
            Criteria:
            1. Covers all aspects of the original problem
            2. Minimizes unsupported assumptions
            3. Maximizes use of given constraints and data
            4. Subproblems are clearly defined and independently verifiable
            5. Dependencies form a valid directed acyclic graph
            If multiple paths have complementary strengths, SYNTHESIZE a hybrid decomposition.
            Output the final decomposition as a list of subproblem dictionaries.""",
            contexts_list=[str(d) for d in decomposition_attempts]
        )

        # Parse chosen decomposition (assuming it's returned as string representation of list)
        # In practice, you'd use ast.literal_eval or JSON parsing; here we simulate
        # For robustness, we'll regenerate if parsing fails
        try:
            import ast
            subproblems = ast.literal_eval(chosen_decomposition)
            if not isinstance(subproblems, list):
                raise ValueError("Not a list")
        except:
            # Fallback: generate a default decomposition
            subproblems = await self.decompose(
                instruction="""Generate a robust, dependency-aware decomposition:
                - Identify core mathematical objects and relationships
                - Break into 3-7 subproblems with clear inputs and outputs
                - Ensure dependencies are acyclic and resolvable
                - Include at least one computational and one conceptual subproblem""",
                context=""
            )

        # STEP 3: Topological sort of subproblems by dependencies
        # Build dependency graph
        id_to_subproblem = {sp['id']: sp for sp in subproblems}
        dependency_graph = {sp['id']: sp.get('dependencies', "").split(',') if sp.get('dependencies') else [] for sp in subproblems}
        
        # Simple topological sort (Kahn's algorithm)
        in_degree = {node: 0 for node in dependency_graph}
        for deps in dependency_graph.values():
            for dep in deps:
                dep = dep.strip()
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [node for node in in_degree if in_degree[node] == 0]
        sorted_order = []
        
        while queue:
            current = queue.pop(0)
            sorted_order.append(current)
            for node, deps in dependency_graph.items():
                if current in [d.strip() for d in deps]:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        
        if len(sorted_order) != len(subproblems):
            # Cycle detected - use original order as fallback
            sorted_order = [sp['id'] for sp in subproblems]

        # STEP 4: Solve subproblems in topological order with verification
        solutions = {}
        max_retries = 3
        
        for sub_id in sorted_order:
            subproblem = id_to_subproblem[sub_id]
            context_so_far = "\n".join([f"Subproblem {k}: {v}" for k, v in solutions.items()])
            
            # Classify subproblem type to route appropriately
            classification = await self.generate(
                instruction=f"""Classify this subproblem for routing:
                Subproblem: {subproblem['description']}
                Context so far: {context_so_far}
                
                Classify as one of:
                - COMPUTATIONAL: Requires numerical calculation, iteration, or algorithm
                - CONCEPTUAL: Requires proof, derivation, or symbolic manipulation
                - TRANSFORMATION: Requires change of representation (e.g., coordinate system, modular arithmetic)
                
                Respond ONLY with the classification keyword.""",
                context=context_so_far
            )
            
            solution = None
            attempts = 0
            
            while attempts < max_retries:
                attempts += 1
                
                if "COMPUTATIONAL" in classification.upper():
                    solution_attempt = await self.programmer(
                        instruction=f"""Solve this computational subproblem:
                        {subproblem['description']}
                        
                        Context from previous subproblems:
                        {context_so_far}
                        
                        Requirements:
                        - Use exact arithmetic (no floating point unless unavoidable)
                        - Validate intermediate results
                        - Return final answer as integer or simplified fraction
                        - Include error checking for edge cases""",
                        context=context_so_far,
                        max_retries=1
                    )
                else:
                    solution_attempt = await self.generate(
                        instruction=f"""Solve this mathematical subproblem:
                        {subproblem['description']}
                        
                        Context from previous subproblems:
                        {context_so_far}
                        
                        Requirements:
                        - Show all logical steps
                        - Justify non-obvious insights
                        - Maintain mathematical rigor
                        - Box final answer for this subproblem""",
                        context=context_so_far
                    )
                
                # Verify solution
                verification = await self.revise(
                    instruction=f"""VERIFY this solution for subproblem {sub_id}:
                    Subproblem: {subproblem['description']}
                    Proposed Solution: {solution_attempt}
                    Context: {context_so_far}
                    
                    Check for:
                    - Mathematical consistency with previous results
                    - Violation of problem constraints
                    - Arithmetic or logical errors
                    - Unjustified assumptions
                    
                    If valid, respond with 'VERIFIED: [summary]'.
                    If invalid, respond with 'INVALID: [detailed critique]' and suggest correction.""",
                    context=solution_attempt
                )
                
                if "VERIFIED" in verification.upper():
                    solution = solution_attempt
                    break
                else:
                    # Use revision to improve
                    solution = await self.revise(
                        instruction=f"""Correct the solution based on this critique:
                        {verification}
                        
                        Maintain mathematical rigor and alignment with subproblem requirements.""",
                        context=solution_attempt
                    )
            
            solutions[sub_id] = solution

        # STEP 5: Synthesize final answer from all subproblem solutions
        synthesis_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in solutions.items()])
        
        final_answer_draft = await self.generate(
            instruction=f"""Synthesize final answer from all subproblem solutions:
            {synthesis_context}
            
            Requirements:
            - Combine results according to problem's ultimate question
            - Ensure final answer is an integer between 000 and 999
            - If answer is a fraction m/n, compute m+n as final answer
            - Double-check against original problem statement
            - Present ONLY the final integer answer, no explanation""",
            context=synthesis_context
        )

        # STEP 6: Final validation and formatting
        final_answer = await self.revise(
            instruction="""Validate and format final answer:
            - Must be an integer between 000 and 999
            - If fraction was involved, ensure m+n was computed correctly
            - Remove any units, explanations, or markdown
            - If answer is invalid, recompute from subproblem solutions
            
            Output ONLY the 3-digit integer (e.g., '123', '007', '999').""",
            context=final_answer_draft
        )

        # Extract just the integer (robustly)
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            answer_int = int(match.group(1))
            if 0 <= answer_int <= 999:
                return f"{answer_int:03d}"  # Zero-pad to 3 digits
        
        # Fallback: return 000 if all else fails (shouldn't happen in robust workflow)
        return "000"