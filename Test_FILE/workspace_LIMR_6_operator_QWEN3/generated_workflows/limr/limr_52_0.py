# Workflow ID: limr_52_0
# Benchmark: limr
# Data Indices: [57, 1]

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
        from collections import defaultdict

        # PHASE 1: PARALLEL INSIGHT GENERATION & PROBLEM DECOMPOSITION
        # Launch two parallel tracks: one for decomposition, one for creative insights
        decomposition_task = self.decompose(
            instruction="""Break this mathematical problem into the smallest logically independent subproblems.
            For each subproblem:
            - Clearly state what needs to be calculated or proven
            - Identify any dependencies on other subproblems
            - Classify the mathematical domain (algebra, geometry, combinatorics, number theory, etc.)
            - Estimate the complexity (low, medium, high)
            Return as structured list with keys: id, description, dependencies, domain, complexity""",
            context=""
        )

        insight_task = self.generate(
            instruction="""Propose 3 radically different perspectives, transformations, or substitutions that could potentially simplify or reframe this entire problem.
            For each insight:
            - Describe the transformation clearly
            - Explain why it might be powerful
            - Estimate the probability (0-100%) that this insight leads to a complete solution
            Format as numbered list with clear headings for each insight.""",
            context=""
        )

        decomposition_result, insight_result = await asyncio.gather(decomposition_task, insight_task)

        # PHASE 2: INSIGHT EVALUATION - SHOULD WE ABANDON DECOMPOSITION FOR A SHORTCUT?
        insight_evaluation = await self.ensemble(
            instruction="""Evaluate these creative insights for their potential to dramatically simplify the problem.
            Select the single most promising insight based on:
            - Mathematical soundness
            - Potential to reduce complexity
            - Probability of success
            - Elegance and generality
            If any insight has >70% estimated success probability AND is mathematically sound, recommend abandoning decomposition and pursuing this insight.
            Otherwise, recommend proceeding with decomposition.
            Return either: "PROCEED_WITH_DECOMPOSITION" or "USE_INSIGHT_[NUMBER]".""",
            contexts_list=[insight_result]
        )

        # PHASE 3A: IF HIGH-VALUE INSIGHT FOUND, PURSUE IT
        if "USE_INSIGHT" in insight_evaluation:
            insight_number = insight_evaluation.split("_")[-1]
            selected_insight = await self.generate(
                instruction=f"""Extract insight number {insight_number} from the following text and expand it into a complete solution strategy:
                {insight_result}
                
                Develop a step-by-step plan leveraging this insight to solve the entire problem.
                Include specific calculations, transformations, or proofs needed.
                Be meticulous and show all work.""",
                context=insight_result
            )

            # Attempt solution via insight path
            draft_solution = await self.generate(
                instruction="""Execute the solution plan described above. Show all mathematical steps, calculations, and reasoning.
                Ensure the final answer is an integer between 000 and 999 as required.
                Box the final answer at the end.""",
                context=selected_insight
            )

            # Validate and revise
            validated_solution = await self.revise(
                instruction="""Critically review this solution:
                - Verify all mathematical steps are correct
                - Check that the final answer is an integer 000-999
                - Ensure no steps are skipped or assumed
                - Confirm the solution actually addresses the original problem
                If any issues are found, correct them and explain the correction.""",
                context=draft_solution
            )

            return validated_solution

        # PHASE 3B: PROCEED WITH DECOMPOSITION (DEFAULT PATH)
        # Parse decomposition result (assuming it's a list of dicts)
        subproblems = decomposition_result  # Already structured from Decompose operator

        # Build dependency graph
        dependency_graph = {sp['id']: sp.get('dependencies', '').split(',') if sp.get('dependencies') else [] for sp in subproblems}
        solutions = {}  # Store solutions by subproblem ID

        # Topological sort to determine execution order
        def topological_sort(graph):
            in_degree = defaultdict(int)
            for node, deps in graph.items():
                for dep in deps:
                    if dep.strip():  # Skip empty dependencies
                        in_degree[node] += 1
            queue = [node for node in graph if in_degree[node] == 0]
            result = []
            while queue:
                node = queue.pop(0)
                result.append(node)
                for other_node, deps in graph.items():
                    if node in [d.strip() for d in deps if d.strip()]:
                        in_degree[other_node] -= 1
                        if in_degree[other_node] == 0:
                            queue.append(other_node)
            return result

        execution_order = topological_sort(dependency_graph)

        # Process subproblems in dependency order
        for sp_id in execution_order:
            sp = next(s for s in subproblems if s['id'] == sp_id)
            
            # Build context from dependencies
            dependency_context = "\n".join([f"Solution to {dep}: {solutions.get(dep, 'Not solved yet')}" 
                                          for dep in dependency_graph[sp_id] if dep.strip()])

            # Classify subproblem type and choose strategy
            strategy = await self.generate(
                instruction=f"""Given this subproblem:
                {sp['description']}
                
                And its mathematical domain: {sp.get('domain', 'unknown')}
                
                Recommend the optimal solving strategy:
                - If computational (calculations, equations, etc.): use PROGRAMMER
                - If requires proof, logical reasoning, or symbolic manipulation: use GENERATE+REVISE
                - If combinatorial/probabilistic with multiple cases: use ENSEMBLE over parallel GENERATE attempts
                
                Also specify any special instructions for the chosen strategy.
                Return format: "STRATEGY: [PROGRAMMER|GENERATE_REVISE|ENSEMBLE] | INSTRUCTIONS: [detailed instructions]".""",
                context=dependency_context
            )

            # Execute chosen strategy
            if "PROGRAMMER" in strategy:
                # Extract instructions for programmer
                prog_instructions = strategy.split("INSTRUCTIONS:")[-1].strip() if "INSTRUCTIONS:" in strategy else "Solve the subproblem with precise computation."
                
                solution_attempt = await self.programmer(
                    instruction=f"""{prog_instructions}
                    
                    Subproblem context: {sp['description']}
                    Dependency solutions: {dependency_context}
                    
                    Return only the final numerical result or key conclusion needed for the next steps.""",
                    context=dependency_context
                )
                
            elif "ENSEMBLE" in strategy:
                # Generate multiple solution attempts in parallel
                attempts = await asyncio.gather(
                    self.generate(instruction=f"Solve this subproblem using combinatorial approach: {sp['description']}\nContext: {dependency_context}", context=dependency_context),
                    self.generate(instruction=f"Solve this subproblem using probabilistic approach: {sp['description']}\nContext: {dependency_context}", context=dependency_context),
                    self.generate(instruction=f"Solve this subproblem using case analysis: {sp['description']}\nContext: {dependency_context}", context=dependency_context)
                )
                
                solution_attempt = await self.ensemble(
                    instruction="""Select the most mathematically sound and complete solution from these attempts.
                    Prioritize solutions that:
                    - Are most rigorous
                    - Have clear step-by-step reasoning
                    - Match the problem's domain and constraints
                    - Yield integer results where appropriate""",
                    contexts_list=attempts
                )
                
            else:  # GENERATE_REVISE path
                draft = await self.generate(
                    instruction=f"""Solve this subproblem with detailed step-by-step reasoning:
                    {sp['description']}
                    
                    Context from dependencies: {dependency_context}
                    
                    Show all work, include all mathematical steps, and justify key insights.""",
                    context=dependency_context
                )
                
                solution_attempt = await self.revise(
                    instruction="""Improve this solution:
                    - Fill any logical gaps
                    - Correct any mathematical errors
                    - Ensure clarity and precision
                    - Verify the conclusion follows from the premises
                    - If the subproblem requires a numerical answer, ensure it's clearly stated""",
                    context=draft
                )

            # Store solution
            solutions[sp_id] = solution_attempt

        # PHASE 4: SYNTHESIZE FINAL ANSWER
        all_solutions_context = "\n\n".join([f"Subproblem {sp_id}: {sol}" for sp_id, sol in solutions.items()])
        
        final_draft = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into a complete, coherent answer to the original problem.
            Original problem: {self.problem_text}
            
            Subproblem solutions:
            {all_solutions_context}
            
            Write a comprehensive solution that:
            - Integrates all subproblem results logically
            - Shows how they combine to answer the original question
            - Clearly states the final answer as an integer between 000 and 999
            - Boxes the final answer at the end
            - Is written in clear, mathematical prose suitable for a competition setting""",
            context=all_solutions_context
        )

        # Final validation and polishing
        final_answer = await self.revise(
            instruction="""Perform final quality assurance:
            - Verify the final answer is an integer between 000 and 999
            - Ensure all steps are mathematically sound
            - Check that the solution actually answers the original problem
            - Improve clarity and flow if needed
            - Remove any redundant or tangential content
            - Ensure the boxed answer is clearly formatted""",
            context=final_draft
        )

        return final_answer