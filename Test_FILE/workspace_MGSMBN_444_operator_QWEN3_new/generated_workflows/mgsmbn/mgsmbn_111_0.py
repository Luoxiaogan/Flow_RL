# Workflow ID: mgsmbn_111_0
# Benchmark: mgsmbn
# Data Indices: [23]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: SEMANTIC DECOMPOSITION & CLASSIFICATION
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math problem. Extract and structure:

1. ENTITIES: List all actors/objects (e.g., people, containers, vehicles) with their roles.
2. QUANTITIES: Extract all explicit numbers and their contextual meaning.
3. RELATIONSHIPS: Translate Bengali relational phrases (e.g., 'অর্ধেকের থেকে 20 বেশি', '25% বেশি') into mathematical expressions or pseudo-code.
4. TARGET: Identify exactly what is being asked (e.g., total, average, difference, final amount).
5. CONSTRAINTS: Note any implicit real-world constraints (e.g., no negative people, integer items).
6. PROBLEM TYPE: Classify as one of: 
   - MULTI_ENTITY_INDEPENDENT (multiple values computed from same base)
   - MULTI_ENTITY_DEPENDENT (values chained sequentially)
   - RATE_PROPORTION (speed, unit price, scaling)
   - SINGLE_EXPRESSION (direct calculation)
   Justify your classification.

Format output as structured JSON-like text with clear section headers.""",
            context=""
        )

        # PHASE 2: ADAPTIVE MODELING STRATEGY
        # Extract problem type for branching
        problem_type_analysis = await self.generate(
            instruction="""From the decomposition, extract ONLY the PROBLEM TYPE classification and justification. 
            Be concise. Format: "TYPE: [type_name] - [brief justification]".""",
            context=decomposition
        )

        # PARALLEL MODELING for independent entities
        if "MULTI_ENTITY_INDEPENDENT" in problem_type_analysis:
            # Extract all entity expressions
            entity_expressions = await self.generate(
                instruction="""From the decomposition, extract ONLY the mathematical expressions for each entity's value.
                List them one per line in format: "EntityX: [expression]". Include the base value if referenced.""",
                context=decomposition
            )
            
            expressions_list = [line.strip() for line in entity_expressions.split('\n') if line.strip() and ':' in line]
            
            # Solve each expression in parallel
            async def solve_expression(expr_line):
                entity_name, expr = expr_line.split(':', 1)
                return await self.generate(
                    instruction=f"""Compute the value for {entity_name} using expression: {expr.strip()}
                    - Show step-by-step arithmetic
                    - Verify no negative/invalid values per constraints
                    - Return ONLY the final number, no text
                    - If error, return 'ERROR: [reason]'""",
                    context=decomposition
                )
            
            computed_values = await asyncio.gather(
                *[solve_expression(expr) for expr in expressions_list]
            )
            
            # Validate and synthesize
            synthesis_context = "\n".join([f"{expressions_list[i]} = {computed_values[i]}" 
                                         for i in range(len(expressions_list))])
            
        # SEQUENTIAL MODELING for dependent entities
        elif "MULTI_ENTITY_DEPENDENT" in problem_type_analysis:
            entity_expressions = await self.generate(
                instruction="""From decomposition, extract mathematical expressions in COMPUTATION ORDER.
                List one per line as "StepN: [expression] - depends on: [previous step]". Resolve dependencies.""",
                context=decomposition
            )
            
            steps = [line.strip() for line in entity_expressions.split('\n') if line.strip() and ':' in line]
            computed_values = []
            
            current_context = decomposition
            for step in steps:
                result = await self.generate(
                    instruction=f"""Compute: {step}
                    - Use previously computed values as needed
                    - Show arithmetic steps
                    - Return ONLY final number
                    - Validate against constraints""",
                    context=current_context
                )
                computed_values.append(result)
                current_context += f"\n{step} RESULT: {result}"
            
            synthesis_context = "\n".join([f"{steps[i]} = {computed_values[i]}" for i in range(len(steps))])
        
        # DIRECT MODELING for rate/proportion/single
        else:
            direct_solution = await self.generate(
                instruction="""Solve the problem directly based on decomposition:
                - Apply appropriate formula (rate, proportion, etc.)
                - Show all steps
                - Validate against constraints
                - Return ONLY final numerical answer""",
                context=decomposition
            )
            synthesis_context = f"DIRECT_SOLUTION: {direct_solution}"

        # PHASE 3: CROSS-VALIDATION & CONSISTENCY CHECK
        validated_solution = await self.ensemble(
            instruction="""Cross-validate the solution:
            1. Verify all referenced values are computed and consistent
            2. Check arithmetic (recalculate key steps)
            3. Ensure final operation (sum/average/etc.) is correctly applied
            4. Confirm answer format (integer/decimal) matches context
            5. Reality check: Does answer make sense? (e.g., no fractional people)
            If any issue, flag and suggest correction. Otherwise, output final answer.
            RETURN ONLY THE FINAL NUMERICAL VALUE OR 'ERROR: [description]'""",
            contexts_list=[synthesis_context, decomposition]
        )

        # PHASE 4: ERROR RECOVERY LOOP (max 2 iterations)
        for attempt in range(2):
            if "ERROR" not in validated_solution:
                break
                
            # Revise based on error
            validated_solution = await self.revise(
                instruction=f"""Fix the error: {validated_solution}
                - Re-examine decomposition and relationships
                - Recompute affected values
                - Maintain constraint compliance
                - Return ONLY corrected numerical value""",
                context=synthesis_context
            )

        # PHASE 5: FINAL EXTRACTION & CLEANUP
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution.
            - Remove all text, units, explanations
            - If decimal, preserve exact precision
            - If multiple numbers, select the one answering the original question
            - Return pure number as string""",
            context=validated_solution
        )

        # Clean and return
        # Remove any remaining non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer)
        # Handle edge case where multiple decimals might appear
        parts = cleaned.split('.')
        if len(parts) > 2:
            cleaned = parts[0] + '.' + ''.join(parts[1:])
        
        return cleaned