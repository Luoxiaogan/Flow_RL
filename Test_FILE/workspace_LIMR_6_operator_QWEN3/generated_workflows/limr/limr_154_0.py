# Workflow ID: limr_154_0
# Benchmark: limr
# Data Indices: [320, 185]

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

        # PHASE 1: Hierarchical Decomposition with Dependency Analysis
        decomposition_instruction = """
        Systematically decompose this mathematical problem into atomic, solvable subproblems.
        For each subproblem:
        - Clearly state what needs to be computed or proven
        - Identify mathematical domain (algebra, number theory, combinatorics, etc.)
        - Specify if it requires computational brute force or conceptual insight
        - List prerequisite subproblems by logical dependency
        - Flag any ambiguities or multiple interpretations
        
        Structure each subproblem as a self-contained unit that can be solved independently once dependencies are met.
        Prioritize decomposition that reveals hidden structure or invariants.
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # If decomposition fails or is empty, fall back to general analysis
        if not subproblems or len(subproblems) == 0:
            fallback_analysis = await self.generate(
                instruction="This problem resists decomposition. Perform holistic analysis: identify key variables, constraints, and potential solution strategies. Propose one complete solution path.",
                context=""
            )
            fallback_revised = await self.revise(
                instruction="Critically verify every step of this solution. Check for algebraic errors, logical gaps, and adherence to problem constraints. Ensure final answer is an integer 000-999.",
                context=fallback_analysis
            )
            return fallback_revised

        # PHASE 2: Topological Sort of Subproblems by Dependency
        # Build dependency graph and sort
        subproblem_dict = {sp['id']: sp for sp in subproblems}
        dependency_graph = {sp['id']: sp['dependencies'].split(',') if sp['dependencies'] else [] for sp in subproblems}
        
        # Simple topological sort (Kahn's algorithm)
        in_degree = {node: 0 for node in dependency_graph.keys()}
        for deps in dependency_graph.values():
            for dep in deps:
                dep = dep.strip()
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [node for node in in_degree if in_degree[node] == 0]
        sorted_subproblems = []
        
        while queue:
            current = queue.pop(0)
            sorted_subproblems.append(subproblem_dict[current])
            for node, deps in dependency_graph.items():
                if current in [d.strip() for d in deps]:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        
        # Handle cyclic dependencies (shouldn't happen in math problems, but defend against)
        if len(sorted_subproblems) != len(subproblems):
            sorted_subproblems = subproblems  # Fallback to original order

        # PHASE 3: Solve Subproblems with Adaptive Strategy
        solutions = {}
        for sp in sorted_subproblems:
            sp_id = sp['id']
            sp_desc = sp['description']
            
            # Classify subproblem type for adaptive handling
            classification = await self.generate(
                instruction=f"""
                Classify this subproblem for optimal solving strategy:
                "{sp_desc}"
                
                Determine:
                1. Is this primarily computational (requires calculation) or conceptual (requires proof/insight)?
                2. Does it have multiple valid interpretations? If so, list them.
                3. What mathematical tools are most appropriate (algebra, calculus, combinatorics, etc.)?
                4. What are the key constraints or boundary conditions?
                
                Output structured classification with clear labels.
                """,
                context=""
            )
            
            # Handle ambiguous subproblems with parallel exploration
            if "multiple interpretations" in classification.lower() or "ambigu" in classification.lower():
                # Generate 2-3 different approaches in parallel
                interpretation_prompts = [
                    f"Approach 1: Solve '{sp_desc}' assuming the most straightforward interpretation. Be explicit about assumptions.",
                    f"Approach 2: Solve '{sp_desc}' considering edge cases or alternative interpretations mentioned in classification: {classification}",
                    f"Approach 3: Solve '{sp_desc}' using a completely different mathematical perspective (e.g., if algebraic, try combinatorial)."
                ]
                
                parallel_attempts = await asyncio.gather(
                    *[self.generate(instruction=prompt, context=classification) for prompt in interpretation_prompts]
                )
                
                # Ensemble to select or synthesize best solution
                sp_solution = await self.ensemble(
                    instruction=f"""
                    Evaluate these parallel solutions to subproblem: {sp_desc}
                    Criteria:
                    1. Mathematical correctness and rigor
                    2. Consistency with original problem constraints
                    3. Clarity and completeness of reasoning
                    4. Computational efficiency (if applicable)
                    
                    Either select the single best solution or synthesize a hybrid that combines strengths.
                    Explicitly justify your choice.
                    """,
                    contexts_list=parallel_attempts
                )
            else:
                # Single interpretation - direct solve with verification
                if "computational" in classification.lower() or "calculate" in classification.lower():
                    # Use programmer for computational subproblems
                    sp_solution = await self.programmer(
                        instruction=f"""
                        Write Python code to solve this mathematical subproblem:
                        {sp_desc}
                        
                        Requirements:
                        - Handle edge cases mentioned in classification: {classification}
                        - Return only the final numerical result (no explanations)
                        - Ensure precision (no floating point errors)
                        - If multiple answers possible, return all as list
                        """,
                        context=classification,
                        max_retries=3
                    )
                else:
                    # Conceptual subproblem - use generate with rigorous revision
                    initial_solution = await self.generate(
                        instruction=f"""
                        Solve this conceptual subproblem with complete mathematical reasoning:
                        {sp_desc}
                        
                        Requirements:
                        - Show all steps of logical derivation
                        - Reference relevant theorems or principles
                        - Handle edge cases from classification: {classification}
                        - Box final answer clearly
                        """,
                        context=classification
                    )
                    sp_solution = await self.revise(
                        instruction=f"""
                        Rigorously verify this solution to: {sp_desc}
                        Checklist:
                        1. Are all mathematical steps logically sound?
                        2. Are all assumptions from classification respected?
                        3. Are boundary conditions properly handled?
                        4. Is the final answer format correct (numerical, 000-999 if applicable)?
                        5. Are there any calculation errors?
                        
                        If errors found, correct them. If solution is solid, enhance clarity and precision.
                        """,
                        context=initial_solution
                    )
            
            # Store solution for dependency resolution
            solutions[sp_id] = sp_solution
            
            # Summarize solution for future context (keep it lean)
            summary_instruction = f"""
            Summarize this subproblem solution for use in dependent subproblems:
            Subproblem: {sp_desc}
            Solution: {sp_solution}
            
            Extract only:
            - Key numerical results or derived formulae
            - Critical constraints or conditions established
            - Any assumptions made
            Format as concise bullet points.
            """
            solutions[sp_id + "_summary"] = await self.summarize(
                instruction=summary_instruction,
                context=sp_solution
            )

        # PHASE 4: Synthesize Final Answer from Subproblem Solutions
        synthesis_context = "\n\n".join([f"Subproblem {sp['id']}: {solutions.get(sp['id'], 'No solution')}" for sp in sorted_subproblems])
        
        final_synthesis = await self.generate(
            instruction=f"""
            Synthesize a complete, coherent solution to the original problem using these subproblem solutions:
            {synthesis_context}
            
            Requirements:
            1. Integrate all subproblem results logically
            2. Ensure global consistency (no contradictions between subproblems)
            3. Derive the final answer as specified in the original problem
            4. Format final answer as an integer between 000 and 999 (zero-pad if necessary)
            5. Include brief justification for final answer
            """,
            context=synthesis_context
        )
        
        # PHASE 5: Final Verification and Formatting
        final_answer = await self.revise(
            instruction="""
            FINAL VERIFICATION AND FORMATTING:
            1. Extract the final numerical answer from the solution.
            2. Verify it is an integer between 000 and 999.
            3. If not, trace back error and recalculate.
            4. Format as exactly three digits with leading zeros (e.g., 5 → 005, 42 → 042, 123 → 123).
            5. If multiple answers possible, select the one most consistent with problem constraints.
            6. Output ONLY the three-digit number, nothing else.
            """,
            context=final_synthesis
        )
        
        # Extract just the three-digit number using regex (defensive programming)
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 999:
                return f"{num:03d}"
        
        # Fallback: return best effort with padding
        return final_answer.strip()[:3].zfill(3) if final_answer.strip().isdigit() else "000"