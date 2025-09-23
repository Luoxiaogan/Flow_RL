# Workflow ID: mgsmbn_85_0
# Benchmark: mgsmbn
# Data Indices: [110]

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

        # PHASE 1: META-ANALYSIS & CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this Bengali math word problem. Identify:
            1. All entities (people, objects, quantities) and their initial states.
            2. All actions/events and their chronological order.
            3. All mathematical relationships (equations, ratios, comparisons).
            4. All constraints (explicit and implicit, e.g., non-negative, integer-only).
            5. The ultimate unknown being asked for.
            6. Potential ambiguities or multiple interpretations.
            Format as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # PHASE 2: STRATEGY ENSEMBLE - GENERATE MULTIPLE APPROACHES
        strategy_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Based on analysis:
                {problem_analysis}
                
                Develop a purely ALGEBRAIC solution strategy:
                - Define variables for unknowns
                - Write equations representing relationships
                - Solve symbolically
                - Substitute known values
                - Show step-by-step symbolic manipulation""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on analysis:
                {problem_analysis}
                
                Develop a PROCEDURAL/STEP-BY-STEP solution strategy:
                - List operations in chronological order
                - Track state changes of entities
                - Handle conditional logic explicitly
                - Show intermediate values at each step
                - Emphasize narrative flow""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on analysis:
                {problem_analysis}
                
                Develop a UNIT-TRACKING & DIMENSIONAL solution strategy:
                - Explicitly label all quantities with units
                - Track unit transformations
                - Verify dimensional consistency at each step
                - Highlight any unit conversions needed
                - Ensure final answer has correct units""",
                context=problem_analysis
            )
        )

        # PHASE 3: SYNTHESIZE BEST STRATEGY
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the three solution approaches into one optimal strategy:
            - Combine algebraic rigor with procedural clarity
            - Incorporate unit tracking for verification
            - Resolve any conflicts between approaches
            - Prioritize strategies that handle edge cases and constraints
            - Output a numbered, ordered list of solution steps with clear dependencies""",
            contexts_list=strategy_approaches
        )

        # PHASE 4: HIERARCHICAL DECOMPOSITION
        subproblems = await self.decompose(
            instruction=f"""Decompose the synthesized strategy into atomic, executable subproblems:
            - Each subproblem should be solvable independently if dependencies are met
            - Specify EXACT dependencies (which subproblem IDs must be solved first)
            - Include expected input and output format for each
            - Handle state transitions explicitly (e.g., "after event X, value Y becomes Z")
            - Format each as: {{ "id": "sp1", "description": "...", "dependencies": "sp0,sp2" }}""",
            context=synthesized_strategy
        )

        # Topological sort of subproblems based on dependencies
        def topological_sort(subproblems_list):
            graph = {sp['id']: sp.get('dependencies', '').split(',') if sp.get('dependencies') else [] for sp in subproblems_list}
            visited = set()
            temp = set()
            result = []
            
            def visit(node_id):
                if node_id in temp:
                    raise ValueError("Circular dependency detected")
                if node_id in visited:
                    return
                temp.add(node_id)
                for dep in graph.get(node_id, []):
                    if dep.strip():
                        visit(dep.strip())
                temp.remove(node_id)
                visited.add(node_id)
                result.append(node_id)
            
            for sp in subproblems_list:
                if sp['id'] not in visited:
                    visit(sp['id'])
            return result

        try:
            sorted_ids = topological_sort(subproblems)
            subproblem_map = {sp['id']: sp for sp in subproblems}
        except:
            # Fallback: use original order if sorting fails
            sorted_ids = [sp['id'] for sp in subproblems]
            subproblem_map = {sp['id']: sp for sp in subproblems}

        # PHASE 5: SOLVE SUBPROBLEMS WITH PARALLEL HYPOTHESES & VALIDATION
        solutions = {}
        for sp_id in sorted_ids:
            sp = subproblem_map[sp_id]
            
            # Generate 3 solution hypotheses in parallel
            hypotheses = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve subproblem using ALGEBRAIC method:
                    Subproblem: {sp['description']}
                    Dependencies solved: {[solutions.get(dep.strip(), 'NOT SOLVED') for dep in sp.get('dependencies', '').split(',') if dep.strip()]}
                    Show all equations and substitutions. Be precise.""",
                    context=str(solutions)
                ),
                self.generate(
                    instruction=f"""Solve subproblem using PROCEDURAL method:
                    Subproblem: {sp['description']}
                    Dependencies solved: {[solutions.get(dep.strip(), 'NOT SOLVED') for dep in sp.get('dependencies', '').split(',') if dep.strip()]}
                    Show step-by-step state changes. Be narrative.""",
                    context=str(solutions)
                ),
                self.generate(
                    instruction=f"""Solve subproblem using UNIT-TRACKING method:
                    Subproblem: {sp['description']}
                    Dependencies solved: {[solutions.get(dep.strip(), 'NOT SOLVED') for dep in sp.get('dependencies', '').split(',') if dep.strip()]}
                    Track all units. Verify consistency. Be meticulous.""",
                    context=str(solutions)
                )
            )
            
            # Ensemble best solution for this subproblem
            best_solution = await self.ensemble(
                instruction=f"""Select the most accurate and complete solution for subproblem: {sp['description']}
                Criteria:
                1. Mathematical correctness
                2. Consistency with dependencies
                3. Unit/dimensional correctness
                4. Alignment with problem constraints
                5. Clarity and traceability
                Return ONLY the final answer value (number) for this subproblem, nothing else.""",
                contexts_list=hypotheses
            )
            
            # Validate and refine solution
            for attempt in range(3):
                validation = await self.revise(
                    instruction=f"""Critically validate this solution:
                    Subproblem: {sp['description']}
                    Proposed Solution: {best_solution}
                    Check for:
                    - Mathematical errors
                    - Violation of constraints (e.g., negative quantities, fractional people)
                    - Inconsistency with problem narrative
                    - Unit mismatches
                    If valid, return "VALID: <solution>". If invalid, return "INVALID: <detailed critique>".""",
                    context=best_solution
                )
                
                if "VALID:" in validation:
                    # Extract validated solution
                    solutions[sp_id] = validation.split("VALID:")[1].strip()
                    break
                else:
                    # Revise based on critique
                    best_solution = await self.revise(
                        instruction=f"""Revise solution based on critique:
                        Critique: {validation}
                        Original Solution: {best_solution}
                        Subproblem: {sp['description']}
                        Fix all identified issues. Return ONLY the corrected numerical value.""",
                        context=best_solution
                    )
            else:
                # If all retries fail, use last attempt
                solutions[sp_id] = best_solution

        # PHASE 6: FINAL COMPUTATION & VERIFICATION
        final_computation_context = f"""
        Problem Analysis: {problem_analysis}
        Synthesized Strategy: {synthesized_strategy}
        All Subproblem Solutions: {solutions}
        """

        final_answer = await self.programmer(
            instruction=f"""Compute the final numerical answer using the subproblem solutions.
            Context: {final_computation_context}
            
            Steps:
            1. Extract all subproblem results.
            2. Apply any final combining operations.
            3. Ensure unit consistency.
            4. Round appropriately if needed (match problem's precision).
            5. Return ONLY the final number (integer or decimal), nothing else.
            
            Generate Python code that computes the answer from the subproblem values.
            Do not use external libraries. Use only basic arithmetic.
            Print only the final numerical result.""",
            context=final_computation_context,
            max_retries=3
        )

        # Extract just the number from programmer output
        number_match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if number_match:
            return number_match.group(0)
        else:
            # Fallback: return as-is if no number found (let evaluation handle it)
            return final_answer.strip()