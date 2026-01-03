# Workflow ID: mgsmbn_11_0
# Benchmark: mgsmbn
# Data Indices: [94, 198]

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

        # Step 1: Classify problem complexity to adapt workflow depth
        complexity_analysis = await self.generate(
            instruction="""Analyze this Bengali math word problem and classify its complexity:
            - Count distinct numerical values, entities, and operations
            - Identify if there are hidden steps or implicit calculations
            - Determine if multiple entities or time sequences are involved
            - Classify as: 
              1 (Simple): Direct calculation with no hidden steps
              2 (Medium): 1-2 hidden steps or unit conversions
              3 (Complex): Multiple dependencies, ambiguous phrasing, or multi-entity tracking
            - Also extract: target unit, expected answer type (integer/decimal), and any constraints
            Return JSON format: {"complexity": int, "target_unit": str, "answer_type": str, "constraints": list}""",
            context=""
        )

        try:
            complexity_data = json.loads(complexity_analysis)
            complexity_level = complexity_data.get("complexity", 2)
        except:
            complexity_level = 2  # Default to medium if parsing fails

        # Step 2: Entity and relationship extraction (foundation for all paths)
        entity_extraction = await self.generate(
            instruction="""Extract all mathematical entities and relationships from the Bengali problem:
            - List all quantities with their units and descriptions
            - Identify all actions (increase, decrease, distribute, compare, etc.)
            - Map relationships between entities (e.g., 'each container has 5 cars')
            - Note any time sequences or conditional statements
            - Format as structured list with clear labels for each component
            - Preserve original Bengali terms with English translations in parentheses""",
            context=""
        )

        # Step 3: Adaptive workflow branching based on complexity
        if complexity_level == 1:
            # Simple path: Direct calculation
            solution_code = await self.programmer(
                instruction=f"""Generate Python code to solve this problem directly:
                Problem context: {entity_extraction}
                Requirements:
                - Use only basic arithmetic operations
                - Track units in comments
                - Output must be a single numerical value
                - No external libraries
                - Include validation that result is positive and matches expected type""",
                context=entity_extraction
            )
            
            final_answer = solution_code

        elif complexity_level == 2:
            # Medium path: Decompose then solve
            decomposition = await self.decompose(
                instruction=f"""Break this problem into minimal necessary subproblems:
                Context: {entity_extraction}
                Requirements:
                - Each subproblem must compute exactly one intermediate value
                - Specify dependencies between subproblems
                - Include unit tracking for each step
                - Final subproblem must produce the answer
                - Handle any implicit calculations (e.g., totals, differences)""",
                context=entity_extraction
            )

            # Solve subproblems in dependency order
            solved_values = {}
            for subproblem in decomposition:
                dep_ids = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                # Wait for dependencies
                dep_context = "\n".join([f"{dep_id}: {solved_values.get(dep_id, 'UNKNOWN')}" for dep_id in dep_ids if dep_id])
                
                sub_solution = await self.programmer(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    Dependencies: {dep_context}
                    Requirements:
                    - Use only given values and dependencies
                    - Track units
                    - Return single numerical value
                    - Validate against constraints""",
                    context=f"Entity context: {entity_extraction}\nDependencies: {dep_context}"
                )
                solved_values[subproblem['id']] = sub_solution

            final_answer = solved_values.get(decomposition[-1]['id'], "") if decomposition else ""

        else:  # complexity_level == 3
            # Complex path: Full layered workflow with validation and ensemble
            decomposition = await self.decompose(
                instruction=f"""Break this complex problem into atomic, verifiable subproblems:
                Context: {entity_extraction}
                Requirements:
                - Identify all implicit assumptions and validate them
                - Handle potential ambiguities in Bengali phrasing
                - Create subproblems for validation checks (e.g., 'Is result positive?')
                - Include unit consistency checks at each step
                - Final subproblem must reconcile all intermediate results""",
                context=entity_extraction
            )

            # Group subproblems by dependency level for parallel solving
            dependency_groups = {}
            for subproblem in decomposition:
                dep_count = len(subproblem.get('dependencies', '').split(',')) if subproblem.get('dependencies') else 0
                if dep_count not in dependency_groups:
                    dependency_groups[dep_count] = []
                dependency_groups[dep_count].append(subproblem)

            solved_values = {}
            for level in sorted(dependency_groups.keys()):
                level_subproblems = dependency_groups[level]
                
                # Solve this level in parallel
                async def solve_subproblem(subp):
                    dep_ids = subp.get('dependencies', '').split(',') if subp.get('dependencies') else []
                    dep_context = "\n".join([f"{dep_id}: {solved_values.get(dep_id, 'UNKNOWN')}" for dep_id in dep_ids if dep_id])
                    
                    return await self.programmer(
                        instruction=f"""Solve with validation:
                        {subp['description']}
                        Dependencies: {dep_context}
                        Requirements:
                        - Validate inputs before computation
                        - Check unit consistency
                        - Return error if constraints violated
                        - Output must be numerical""",
                        context=f"Entities: {entity_extraction}\nDeps: {dep_context}"
                    )

                results = await asyncio.gather(*[solve_subproblem(sp) for sp in level_subproblems])
                for i, subp in enumerate(level_subproblems):
                    solved_values[subp['id']] = results[i]

            # Generate multiple solution approaches for final answer
            solution_approaches = await asyncio.gather(
                self.programmer(
                    instruction=f"""Approach 1: Direct calculation from decomposition
                    Use values: {json.dumps(solved_values)}
                    Compute final answer with explicit formula""",
                    context=entity_extraction
                ),
                self.programmer(
                    instruction=f"""Approach 2: Step-by-step accumulation
                    Re-calculate final answer by simulating the process chronologically
                    Use intermediate values: {json.dumps(solved_values)}""",
                    context=entity_extraction
                ),
                self.generate(
                    instruction=f"""Approach 3: Logical reasoning path
                    Derive answer through proportional reasoning or algebraic manipulation
                    Show all steps and verify against decomposition results: {json.dumps(solved_values)}""",
                    context=entity_extraction
                )
            )

            # Ensemble to select best answer
            final_answer = await self.ensemble(
                instruction="""Select the most reliable answer:
                - Compare numerical results from all approaches
                - Prefer answers that match across methods
                - Validate against problem constraints and units
                - Ensure answer is single numerical value
                - If conflict, choose the one with clearest derivation and validation""",
                contexts_list=solution_approaches
            )

        # Final validation and extraction
        validated_answer = await self.revise(
            instruction="""Extract and validate the final numerical answer:
            - Ensure output is a single number (integer or decimal)
            - Remove any units, text, or explanations
            - Verify it's positive and contextually plausible
            - If multiple numbers, select the one that answers the question
            - Return ONLY the number, nothing else""",
            context=final_answer
        )

        return validated_answer