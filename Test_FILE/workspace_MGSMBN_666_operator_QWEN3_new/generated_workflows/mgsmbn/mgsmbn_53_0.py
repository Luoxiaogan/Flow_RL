# Workflow ID: mgsmbn_53_0
# Benchmark: mgsmbn
# Data Indices: [88, 169]

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
        from collections import defaultdict, deque

        # Phase 1: Problem Classification
        classification = await self.generate(
            instruction="""Thoroughly classify this Bengali math word problem by analyzing its structure and requirements. Consider:
            - Is it primarily about rates (speed, leakage, production over time)?
            - Does it involve algebraic relationships with unknowns?
            - Is it a distribution or sharing problem?
            - Does it require proportional reasoning (ratios, percentages)?
            - Is it a simple arithmetic combination or comparison?
            Quote specific phrases from the problem that justify your classification.
            Also identify: 
            - The target unknown (what is being asked)
            - Key numerical values and their meanings
            - Units of measurement involved
            - Any constraints or conditions mentioned
            Format your response as a structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Dynamic Decomposition based on classification
        decomposition = await self.decompose(
            instruction=f"""Based on this classification:
            {classification}
            
            Decompose the problem into essential subproblems. For each subproblem:
            - Clearly state what needs to be calculated or determined
            - Specify any dependencies (which other subproblems must be solved first)
            - Indicate whether it requires symbolic reasoning, numerical calculation, or unit conversion
            - Note any real-world constraints that apply (e.g., no negative quantities)
            
            Structure each subproblem with:
            id: unique identifier (e.g., "step1", "step2")
            description: clear task description
            dependencies: comma-separated list of prerequisite subproblem IDs (empty if none)""",
            context=classification
        )

        # Build dependency graph and topological sort
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        subproblem_map = {sp['id']: sp for sp in decomposition}
        
        for sp in decomposition:
            deps = [d.strip() for d in sp['dependencies'].split(',') if d.strip()]
            for dep in deps:
                graph[dep].append(sp['id'])
                in_degree[sp['id']] += 1
        
        # Initialize queue with nodes having no dependencies
        queue = deque([sp['id'] for sp in decomposition if in_degree[sp['id']] == 0])
        sorted_order = []
        
        while queue:
            current = queue.popleft()
            sorted_order.append(current)
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Phase 3: Parallel Subproblem Resolution with Validation
        subproblem_results = {}
        
        for wave in range(len(sorted_order)):
            # Get all subproblems ready to be solved in this wave
            current_wave = [sp_id for sp_id in sorted_order if all(dep in subproblem_results for dep in [d.strip() for d in subproblem_map[sp_id]['dependencies'].split(',') if d.strip()])]
            
            if not current_wave:
                break
                
            # Process current wave in parallel
            async def solve_subproblem(sp_id):
                sp = subproblem_map[sp_id]
                context_so_far = "\n".join([f"{k}: {v}" for k, v in subproblem_results.items()])
                
                # Choose strategy based on subproblem type
                if "calculate" in sp['description'].lower() or "compute" in sp['description'].lower() or any(op in sp['description'] for op in ["+", "-", "*", "/"]):
                    # Use programmer for numerical computation
                    result = await self.programmer(
                        instruction=f"""Solve this subproblem:
                        {sp['description']}
                        
                        Context from previous steps:
                        {context_so_far}
                        
                        Extract all necessary values from the original problem and previous results.
                        Write clean, well-commented Python code that computes the result.
                        Handle unit conversions if needed.
                        Return only the numerical result, no explanations.""",
                        context=context_so_far
                    )
                else:
                    # Use generate for symbolic or reasoning steps
                    result = await self.generate(
                        instruction=f"""Solve this subproblem through reasoning:
                        {sp['description']}
                        
                        Context from previous steps:
                        {context_so_far}
                        
                        Show your step-by-step reasoning.
                        If assigning variables, clearly define them.
                        If setting up equations, write them explicitly.
                        Your final output should be the specific answer to this subproblem, clearly stated.""",
                        context=context_so_far
                    )
                
                # Validate and revise the result
                validated = await self.revise(
                    instruction=f"""Critically validate this subproblem solution:
                    Subproblem: {sp['description']}
                    Proposed solution: {result}
                    
                    Check for:
                    - Arithmetic or logical errors
                    - Unit consistency with original problem
                    - Adherence to real-world constraints (no negative quantities, etc.)
                    - Consistency with previous subproblem results
                    
                    If any issues are found, correct them and explain the fix.
                    If no issues, return the solution unchanged with 'VALIDATED:' prefix.""",
                    context=result
                )
                
                return sp_id, validated
            
            # Execute current wave in parallel
            tasks = [solve_subproblem(sp_id) for sp_id in current_wave]
            results = await asyncio.gather(*tasks)
            
            # Store results
            for sp_id, result in results:
                subproblem_results[sp_id] = result
        
        # Phase 4: Final Synthesis and Computation
        synthesis_context = "\n".join([f"{k}: {v}" for k, v in subproblem_results.items()])
        
        final_answer = await self.programmer(
            instruction=f"""Using all subproblem results:
            {synthesis_context}
            
            Compute the final numerical answer to the original question.
            Ensure all values are correctly substituted.
            Handle any final unit conversions if needed.
            Return ONLY the numerical result, no units, no explanations, no text.
            If the answer is a decimal, round appropriately based on context.
            If multiple answers are possible, choose the most reasonable based on constraints.""",
            context=synthesis_context
        )
        
        # Phase 5: Ensemble Fallback for Ambiguity or Low Confidence
        # Check if final answer seems problematic (contains text, multiple values, etc.)
        if not self._is_valid_number(final_answer):
            # Generate alternative approaches
            alternatives = await asyncio.gather(
                self.generate(instruction="Solve this problem using direct arithmetic approach", context=""),
                self.generate(instruction="Solve this problem using algebraic equation setup", context=""),
                self.generate(instruction="Solve this problem using proportional reasoning", context="")
            )
            
            # Extract numerical answers from alternatives
            extracted_answers = []
            for alt in alternatives:
                extracted = await self.programmer(
                    instruction="Extract only the numerical answer from this solution. If no clear number, return 'INVALID'",
                    context=alt
                )
                if self._is_valid_number(extracted):
                    extracted_answers.append(extracted)
            
            if len(extracted_answers) > 0:
                # Use ensemble to select best answer
                final_answer = await self.ensemble(
                    instruction="""Select the most appropriate numerical answer from these candidates.
                    Consider which solution:
                    - Matches all given constraints in the original problem
                    - Has the clearest and most logical derivation
                    - Is most consistent with real-world expectations
                    Return ONLY the selected numerical value, nothing else.""",
                    contexts_list=extracted_answers
                )
        
        return final_answer.strip()
    
    def _is_valid_number(self, text):
        """Helper to check if text contains a valid number"""
        if not isinstance(text, str):
            return False
        text = text.strip()
        if not text:
            return False
        try:
            float(text)
            return True
        except ValueError:
            return False