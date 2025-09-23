# Workflow ID: mgsmbn_130_0
# Benchmark: mgsmbn
# Data Indices: [98]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarpose(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import json

        # Step 1: Generate multiple interpretive perspectives in parallel
        perspective_instructions = [
            "Interpret this problem chronologically: Identify events in sequence, their temporal relationships, and how quantities change over time. Extract explicit and implicit time markers (e.g., 'পরবর্তী দুইদিন', 'বাকি সপ্তাহ'). Structure output as a timeline with quantities at each step.",
            "Interpret this problem mathematically: Identify all numerical entities, their relationships (ratios, differences, totals), and required operations. Ignore narrative and focus purely on quantitative structure. List variables, equations, and unknowns.",
            "Interpret this problem through constraints: Identify all boundary conditions, physical/logical limitations (e.g., non-negative quantities), and implicit rules (e.g., 'বাকি সপ্তাহ' implies 7 minus already mentioned days). List constraints explicitly."
        ]
        
        perspectives = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in perspective_instructions]
        )

        # Step 2: Ensemble perspectives into unified decomposition plan
        decomposition_plan = await self.ensemble(
            instruction="""Synthesize the three perspectives into a single, coherent decomposition plan. 
            Prioritize chronological sequence but integrate mathematical relationships and constraints. 
            Output must be a numbered list of subproblems, each with:
            - Clear description of what to calculate
            - Dependencies on previous subproblems (if any)
            - Expected unit of measurement
            - Confidence level (High/Medium/Low) based on clarity in original text""",
            contexts_list=perspectives
        )

        # Step 3: Decompose using the synthesized plan
        subproblems = await self.decompose(
            instruction=f"""Decompose the problem using this plan:
            {decomposition_plan}
            
            For each subproblem:
            - Assign a unique ID (e.g., SP1, SP2)
            - Specify dependencies using IDs (comma-separated)
            - Flag if unit conversion is needed
            - Flag if requires algebraic modeling (unknown variables)""",
            context=decomposition_plan
        )

        # Step 4: Solve each subproblem with conditional strategy
        subproblem_solutions = {}
        subproblem_metadata = {}

        for sp in subproblems:
            sp_id = sp['id']
            sp_desc = sp['description']
            dependencies = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
            
            # Wait for dependencies
            if dependencies and dependencies[0]:
                await asyncio.gather(*[asyncio.sleep(0) for dep in dependencies if dep in subproblem_solutions])
            
            # Classify subproblem type
            classification = await self.generate(
                instruction=f"""Classify this subproblem for optimal solving strategy:
                Subproblem: {sp_desc}
                
                Choose ONE strategy:
                A) DIRECT_NARRATIVE: Can be solved by direct arithmetic from text (e.g., '2 ঘণ্টা কম' → subtract 2)
                B) COMPUTATIONAL: Requires algebraic modeling or iterative calculation (e.g., solving for unknown, unit conversion)
                C) CONSTRAINT_VALIDATION: Primarily about checking boundaries or conditions
                
                Also specify:
                - Required unit: [unit name]
                - Critical entities: [list of key numbers/entities]
                - Potential pitfalls: [what could go wrong in calculation]""",
                context=sp_desc
            )
            
            subproblem_metadata[sp_id] = {
                'classification': classification,
                'unit': None,
                'entities': []
            }
            
            # Extract unit and entities from classification (simplified parsing)
            if 'Required unit:' in classification:
                unit_line = [line for line in classification.split('\n') if 'Required unit:' in line][0]
                subproblem_metadata[sp_id]['unit'] = unit_line.split('Required unit:')[-1].strip()
            
            # Solve based on classification
            if 'DIRECT_NARRATIVE' in classification:
                solution = await self.generate(
                    instruction=f"""Solve this subproblem using direct narrative reasoning:
                    {sp_desc}
                    
                    Use only information explicitly stated or trivially inferred.
                    Show step-by-step arithmetic.
                    Final answer must be a single number with unit: {subproblem_metadata[sp_id]['unit']}""",
                    context=sp_desc
                )
            elif 'COMPUTATIONAL' in classification:
                # Generate two parallel code solutions
                code_attempts = await asyncio.gather(
                    self.programmer(
                        instruction=f"""Generate Python code for this subproblem:
                        {sp_desc}
                        
                        Approach 1: Literal translation - convert Bengali narrative directly to code operations.
                        Use variable names based on entities mentioned.
                        Include unit tracking in comments.
                        Return only the numerical result.""",
                        context=sp_desc
                    ),
                    self.programmer(
                        instruction=f"""Generate Python code for this subproblem:
                        {sp_desc}
                        
                        Approach 2: Abstract modeling - define variables for unknowns, set up equations, solve algebraically.
                        Include validation checks for constraints.
                        Return only the numerical result.""",
                        context=sp_desc
                    )
                )
                
                # Ensemble code solutions
                solution = await self.ensemble(
                    instruction=f"""Choose the most reliable solution from these two code attempts:
                    Attempt 1: {code_attempts[0]}
                    Attempt 2: {code_attempts[1]}
                    
                    Consider:
                    - Which better handles implicit constraints?
                    - Which maintains unit consistency?
                    - Which matches the chronological sequence?
                    
                    Output ONLY the final numerical result with unit: {subproblem_metadata[sp_id]['unit']}""",
                    contexts_list=code_attempts
                )
            else:  # CONSTRAINT_VALIDATION
                solution = await self.generate(
                    instruction=f"""Validate this constraint subproblem:
                    {sp_desc}
                    
                    Output either:
                    - The validated quantity (if constraint is satisfied)
                    - 0 (if constraint prevents calculation)
                    - Error: [reason] (if constraint is violated)""",
                    context=sp_desc
                )
            
            subproblem_solutions[sp_id] = solution

        # Step 5: Integrate solutions with cross-validation
        integration_context = "\n".join([f"{sp_id}: {sol}" for sp_id, sol in subproblem_solutions.items()])
        
        integrated_solution = await self.revise(
            instruction=f"""Integrate all subproblem solutions into final answer:
            {integration_context}
            
            Validate:
            1. Units are consistent across all subproblems
            2. Temporal sequence is respected
            3. No mathematical contradictions
            4. Answer makes sense in real-world context
            
            If any issue found, flag it and suggest correction.
            Final output must be a single numerical value (integer or decimal) representing the answer.""",
            context=integration_context
        )

        # Step 6: Adversarial validation loop (max 2 iterations)
        final_answer = integrated_solution
        for validation_round in range(2):
            adversary = await self.generate(
                instruction=f"""You are an adversarial validator. Assume this answer is WRONG:
                Proposed Answer: {final_answer}
                Original Problem: {self.problem_text}
                
                Find flaws in:
                - Linguistic interpretation (misread Bengali phrases)
                - Mathematical operations (wrong sequence, missing steps)
                - Unit handling (inconsistent or incorrect units)
                - Constraint violations (negative quantities, impossible scenarios)
                
                If no flaws found, output: "NO ISSUES FOUND"
                Otherwise, output detailed critique and suggested fix.""",
                context=final_answer
            )
            
            if "NO ISSUES FOUND" in adversary or "no flaws" in adversary.lower():
                break
            else:
                # Revise based on critique
                final_answer = await self.revise(
                    instruction=f"""Revise solution based on this critique:
                    {adversary}
                    
                    Maintain all correct parts, fix only identified issues.
                    Output revised numerical answer.""",
                    context=final_answer
                )

        # Step 7: Extract final numerical answer
        answer_extraction = await self.generate(
            instruction=f"""Extract ONLY the final numerical answer from this text:
            {final_answer}
            
            Rules:
            - Must be a single number (integer or decimal)
            - Remove all units, text, and explanations
            - If multiple numbers, choose the one that answers the original question
            - If no clear number, output 0""",
            context=final_answer
        )

        return answer_extraction.strip()