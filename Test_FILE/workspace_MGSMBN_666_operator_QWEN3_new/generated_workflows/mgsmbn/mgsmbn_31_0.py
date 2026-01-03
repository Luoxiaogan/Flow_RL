# Workflow ID: mgsmbn_31_0
# Benchmark: mgsmbn
# Data Indices: [85]

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

        # Step 1: Linguistic Preprocessing - Extract math keywords and resolve ambiguities
        linguistic_context = await self.generate(
            instruction="""Perform deep linguistic analysis of the Bengali math problem:
            1. Identify all mathematical keywords and map to operations (যোগ → +, বিয়োগ → -, গুণ → ×, ভাগ → ÷, শতাংশ → %, etc.)
            2. List all numerical values with their contextual meaning (e.g., "5 ইঞ্চি" → dimension, "3টি" → count)
            3. Flag ambiguous phrases and propose interpretations (e.g., "জনের" → possession vs. per-person)
            4. Identify implied constraints (e.g., non-negative quantities, integer people)
            5. Extract requested answer unit and format
            Output as structured markdown with clear sections.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition with linguistic context
        subproblems = await self.decompose(
            instruction=f"""Decompose this problem using linguistic context:
            {linguistic_context}
            
            Rules:
            - Each subproblem must represent one atomic calculation or logical step
            - Explicitly state dependencies (e.g., "Step 2 needs result from Step 1")
            - Include unit tracking requirements for each step
            - Flag steps requiring conversions or hidden assumptions
            - Output as list of dictionaries with 'id', 'description', 'dependencies'""",
            context=linguistic_context
        )

        # Step 3: Parallel Solution Generation for independent subproblems
        async def solve_subproblem(subproblem):
            # Generate mathematical formulation
            formulation = await self.generate(
                instruction=f"""Convert this subproblem to mathematical formulation:
                Subproblem: {subproblem['description']}
                
                Requirements:
                - Express in symbolic math (variables, formulas)
                - Specify input values and their sources
                - State output variable and expected unit
                - Include error checks (e.g., positivity, range)
                - If dependent on other steps, reference their IDs""",
                context=linguistic_context
            )
            
            # Execute with Programmer
            result = await self.programmer(
                instruction=f"""Execute this mathematical formulation:
                {formulation}
                
                Critical Requirements:
                - Track units throughout calculation
                - Validate intermediate results against physical constraints
                - If unit conversion needed, show explicit step
                - Return only final numerical value with unit""",
                context=formulation,
                max_retries=2
            )
            
            # Validate result
            validated = await self.revise(
                instruction=f"""Validate this result against original problem:
                Subproblem: {subproblem['description']}
                Result: {result}
                
                Check:
                1. Does it match expected unit?
                2. Is it physically plausible (non-negative, reasonable magnitude)?
                3. Does it satisfy dependencies (if any)?
                4. If error found, suggest correction
                
                If valid, return 'VALID: <result>'. If invalid, return 'INVALID: <explanation>'""",
                context=result
            )
            
            if "INVALID" in validated:
                # Retry with correction
                corrected_formulation = await self.revise(
                    instruction=f"""Correct the formulation based on validation error:
                    Original: {formulation}
                    Error: {validated}
                    
                    Provide corrected mathematical formulation with explicit fixes.""",
                    context=formulation
                )
                
                result = await self.programmer(
                    instruction=f"""Execute corrected formulation:
                    {corrected_formulation}
                    
                    Same unit tracking and validation requirements as before.""",
                    context=corrected_formulation,
                    max_retries=1
                )
            
            return {
                'id': subproblem['id'],
                'description': subproblem['description'],
                'result': result,
                'formulation': formulation
            }

        # Solve subproblems respecting dependencies
        results = {}
        solved_ids = set()
        
        # Simple dependency resolution (topological sort would be better for complex cases)
        max_iterations = len(subproblems) * 2
        iteration = 0
        
        while len(solved_ids) < len(subproblems) and iteration < max_iterations:
            iteration += 1
            current_batch = []
            
            for subproblem in subproblems:
                if subproblem['id'] in solved_ids:
                    continue
                    
                deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                deps = [d.strip() for d in deps if d.strip()]
                
                if all(dep in solved_ids for dep in deps):
                    current_batch.append(subproblem)
            
            if not current_batch:
                # Deadlock - solve remaining in parallel as last resort
                remaining = [sp for sp in subproblems if sp['id'] not in solved_ids]
                batch_results = await asyncio.gather(*[solve_subproblem(sp) for sp in remaining])
                for res in batch_results:
                    results[res['id']] = res
                    solved_ids.add(res['id'])
                break
            
            # Solve current independent batch in parallel
            batch_results = await asyncio.gather(*[solve_subproblem(sp) for sp in current_batch])
            for res in batch_results:
                results[res['id']] = res
                solved_ids.add(res['id'])

        # Step 4: Generate multiple solution strategies for final answer
        strategy_contexts = []
        
        # Strategy 1: Direct calculation from subproblem results
        direct_strategy = await self.generate(
            instruction=f"""Synthesize final answer from subproblem results:
            Subproblem Results: {results}
            
            Steps:
            1. Combine results according to problem's final requirement
            2. Show complete calculation chain
            3. Verify unit consistency
            4. Present final numerical answer""",
            context=str(results)
        )
        strategy_contexts.append(direct_strategy)
        
        # Strategy 2: Alternative approach (if applicable)
        alternative_strategy = await self.generate(
            instruction=f"""Propose alternative solution strategy:
            Original Problem: {self.problem_text}
            Linguistic Context: {linguistic_context}
            
            Requirements:
            - Use different mathematical approach (algebraic, proportional, etc.)
            - Show complete working
            - Must arrive at same final unit
            - Include validation against subproblem results""",
            context=linguistic_context
        )
        strategy_contexts.append(alternative_strategy)
        
        # Strategy 3: Unit-first approach
        unit_strategy = await self.generate(
            instruction=f"""Solve by tracking units first:
            Problem: {self.problem_text}
            
            Method:
            1. Start from requested answer unit
            2. Work backwards to determine required operations
            3. Dimensional analysis to verify each step
            4. Calculate final value""",
            context=""
        )
        strategy_contexts.append(unit_strategy)

        # Step 5: Ensemble - Select best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            Criteria:
            1. Numerical consistency across strategies
            2. Completeness of intermediate steps
            3. Unit tracking rigor
            4. Physical plausibility
            5. Clarity of explanation
            
            If all agree, pick most detailed.
            If conflict, pick one with explicit validation.
            Extract ONLY the final numerical answer.""",
            contexts_list=strategy_contexts
        )

        # Step 6: Final sanitization - extract pure numerical value
        final_answer = await self.generate(
            instruction=f"""Extract final numerical answer:
            Solution: {final_solution}
            
            Rules:
            - Remove all text, units, explanations
            - Return only the number (integer or decimal)
            - If decimal, preserve up to 2 decimal places unless problem implies integer
            - No markdown, no formatting, just the number as string""",
            context=final_solution
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer)
        
        # Handle edge case: multiple decimal points
        parts = cleaned.split('.')
        if len(parts) > 2:
            cleaned = parts[0] + '.' + ''.join(parts[1:])
        elif len(parts) == 2:
            cleaned = parts[0] + '.' + parts[1]
        else:
            cleaned = parts[0]
            
        return cleaned.strip()