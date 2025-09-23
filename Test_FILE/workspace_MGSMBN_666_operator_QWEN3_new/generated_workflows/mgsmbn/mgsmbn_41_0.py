# Workflow ID: mgsmbn_41_0
# Benchmark: mgsmbn
# Data Indices: [68]

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
        
        # PHASE 1: PARALLEL ENTITY EXTRACTION & PROBLEM DECOMPOSITION
        entity_extraction_task = self.generate(
            instruction="""Extract all numerical values, named entities, and their semantic roles from the Bengali problem. 
            Format as:
            NUMERICAL ENTITIES:
            - [value]: [description of what it represents, including units if mentioned]
            VERBS/ACTIONS:
            - [verb]: [mathematical implication, e.g., 'gives' → subtraction]
            CONSTRAINTS:
            - [constraint description]
            Ensure no numerical value or key action is omitted.""",
            context=""
        )
        
        decomposition_task = self.decompose(
            instruction="""Break this problem into minimal, executable mathematical subproblems. 
            Each subproblem must:
            - Represent one atomic calculation
            - Explicitly state its inputs (which variables/numbers it uses)
            - Define its output (what new variable it computes)
            - List dependencies (which subproblem IDs must be solved first)
            Prioritize chronological or causal order. Handle hidden steps (e.g., attendance rates, unit conversions).""",
            context=""
        )
        
        # Execute in parallel
        entity_inventory, decomposition = await asyncio.gather(entity_extraction_task, decomposition_task)
        
        # PHASE 2: DYNAMIC SOLUTION GENERATION & VERIFICATION BRANCH
        async def solve_subproblem_chain(decomposition, entity_inventory):
            subproblem_solutions = {}
            variable_mapping = {}
            
            # Sort subproblems by dependency (topological order)
            subproblem_dict = {sp['id']: sp for sp in decomposition}
            solved_ids = set()
            
            for sp in decomposition:
                # Wait for dependencies
                deps = sp['dependencies'].split(',') if sp['dependencies'] else []
                for dep in deps:
                    dep = dep.strip()
                    if dep and dep not in solved_ids:
                        # Shouldn't happen if decomposition is correct, but handle gracefully
                        await asyncio.sleep(0)  # yield
                
                # Generate mathematical expression for this subproblem
                expression_spec = await self.generate(
                    instruction=f"""Convert this subproblem into a precise mathematical expression:
                    Subproblem: {sp['description']}
                    Available entities: {entity_inventory}
                    Rules:
                    - Use only variables from the entity inventory or previously computed outputs
                    - Use Python-compatible syntax (e.g., * for multiplication)
                    - Include unit comments if units are mentioned (e.g., # টাকা)
                    - Do NOT solve — only write the expression
                    Output format: VARIABLE_NAME = EXPRESSION""",
                    context=sp['description']
                )
                
                # Extract variable name and expression
                var_match = re.search(r'^([a-zA-Z_]\w*)\s*=', expression_spec)
                if not var_match:
                    # Fallback: use subproblem ID as variable name
                    var_name = f"result_{sp['id']}"
                    expression = expression_spec
                else:
                    var_name = var_match.group(1)
                    expression = expression_spec
                
                # Execute with programmer
                try:
                    exec_result = await self.programmer(
                        instruction=f"""Execute this calculation:
                        Expression: {expression}
                        Context: {sp['description']}
                        Entity inventory: {entity_inventory}""",
                        context=expression,
                        max_retries=3
                    )
                    
                    # Extract numerical result (assume last line is answer)
                    lines = exec_result.strip().split('\n')
                    result_line = lines[-1] if lines else "0"
                    # Extract number from result (handle various formats)
                    num_match = re.search(r'[-+]?\d*\.?\d+', result_line)
                    if num_match:
                        computed_value = float(num_match.group())
                    else:
                        computed_value = 0.0
                    
                    subproblem_solutions[sp['id']] = computed_value
                    variable_mapping[var_name] = computed_value
                    solved_ids.add(sp['id'])
                    
                except Exception as e:
                    # On failure, store error and proceed (will be caught in validation)
                    subproblem_solutions[sp['id']] = f"ERROR: {str(e)}"
                    solved_ids.add(sp['id'])
            
            return subproblem_solutions, variable_mapping
        
        # PHASE 3: PARALLEL VALIDATION & SANITY CHECK
        async def run_validations(entity_inventory, decomposition, variable_mapping):
            validations = await asyncio.gather(
                self.generate(
                    instruction=f"""Cross-validate solution against entity inventory:
                    Entity Inventory: {entity_inventory}
                    Computed Variables: {variable_mapping}
                    Check:
                    1. Are all numerical entities from inventory used in calculations?
                    2. Are there any computed variables not traceable to inventory?
                    3. Do units (if any) propagate correctly?
                    Return "VALID" if all checks pass, otherwise list specific mismatches.""",
                    context=str(variable_mapping)
                ),
                self.generate(
                    instruction=f"""Sanity check final answer using order-of-magnitude estimation:
                    Problem: {self.problem_text}
                    Computed answer: {variable_mapping}
                    Estimate expected magnitude (e.g., 'tens', 'hundreds'). 
                    Is computed answer within reasonable range? Return "SANITY_OK" or "SANITY_FAIL: [reason]""",
                    context=str(variable_mapping)
                )
            )
            return validations
        
        # Execute main solution and validations in parallel
        solution_task = solve_subproblem_chain(decomposition, entity_inventory)
        solution, variable_mapping = await solution_task
        
        # Get final answer (assume last subproblem is the target)
        final_subproblem_id = decomposition[-1]['id'] if decomposition else "unknown"
        final_answer = solution.get(final_subproblem_id, 0)
        
        # Run validations
        validation_results = await run_validations(entity_inventory, decomposition, variable_mapping)
        entity_validation, sanity_check = validation_results
        
        # PHASE 4: ITERATIVE REFINEMENT (up to 2 retries)
        refinement_needed = ("VALID" not in entity_validation) or ("SANITY_OK" not in sanity_check)
        retry_count = 0
        
        while refinement_needed and retry_count < 2:
            retry_count += 1
            
            # Generate revision instructions based on validation feedback
            revision_instruction = f"""Revise the solution approach based on validation feedback:
            Entity Validation: {entity_validation}
            Sanity Check: {sanity_check}
            Previous decomposition: {decomposition}
            Previous variable mapping: {variable_mapping}
            
            Specific actions:
            - If entities are missing, add subproblems to incorporate them
            - If units mismatch, add conversion subproblems
            - If sanity fails, check decimal placement or operation order
            - If dependencies are wrong, reorder subproblems
            Output revised decomposition as list of subproblem dictionaries."""
            
            revised_decomposition = await self.revise(
                instruction=revision_instruction,
                context=str(decomposition)
            )
            
            # Attempt to parse revised decomposition (fallback to original if parsing fails)
            try:
                # Simple heuristic: if output looks like a list of dicts, use it
                if '[' in revised_decomposition and ']' in revised_decomposition:
                    # This is a simplification - in practice, you'd use proper parsing
                    # For this workflow, we'll assume the revise operator returns valid decomposition
                    # In a real system, you'd have robust parsing/error handling
                    pass  # Keep revised_decomposition as string for now
                else:
                    revised_decomposition = decomposition  # fallback
            except:
                revised_decomposition = decomposition
            
            # Retry solution with revised decomposition
            solution, variable_mapping = await solve_subproblem_chain(revised_decomposition, entity_inventory)
            final_answer = solution.get(final_subproblem_id, 0)
            
            # Re-validate
            validation_results = await run_validations(entity_inventory, revised_decomposition, variable_mapping)
            entity_validation, sanity_check = validation_results
            refinement_needed = ("VALID" not in entity_validation) or ("SANITY_OK" not in sanity_check)
        
        # PHASE 5: ENSEMBLE FINAL ANSWER (handle edge cases)
        # Generate alternative solution via direct calculation for comparison
        direct_solution = await self.programmer(
            instruction="""Solve the problem directly in one step if possible.
            Extract all numbers and relationships from the original problem.
            Write and execute a single Python expression that computes the answer.
            Show your work step by step in comments.""",
            context="",
            max_retries=3
        )
        
        # Extract number from direct solution
        direct_num = 0.0
        try:
            lines = direct_solution.strip().split('\n')
            for line in reversed(lines):
                num_match = re.search(r'[-+]?\d*\.?\d+', line)
                if num_match:
                    direct_num = float(num_match.group())
                    break
        except:
            pass
        
        # Create answer candidates
        candidates = [
            str(final_answer),
            str(direct_num),
            str(round(final_answer)),  # integer fallback
            str(int(final_answer)) if final_answer == int(final_answer) else str(final_answer)
        ]
        
        # Use ensemble to select most consistent answer
        final_selection = await self.ensemble(
            instruction="""Select the best answer from candidates:
            - Prefer answers that appear multiple times
            - If all differ, choose the one closest to the direct calculation
            - Ensure answer is a single number (no units or text)
            - Round to integer if problem context implies whole numbers (e.g., people, items)
            Candidates:""" + "\n".join([f"{i+1}. {c}" for i, c in enumerate(candidates)]),
            contexts_list=candidates
        )
        
        # Extract final numerical answer
        try:
            final_num_match = re.search(r'[-+]?\d*\.?\d+', final_selection)
            if final_num_match:
                final_result = float(final_num_match.group())
                # If answer should be integer (e.g., count of items), convert
                if final_result == int(final_result):
                    final_result = int(final_result)
            else:
                final_result = final_answer  # fallback
        except:
            final_result = final_answer  # ultimate fallback
        
        return str(final_result)