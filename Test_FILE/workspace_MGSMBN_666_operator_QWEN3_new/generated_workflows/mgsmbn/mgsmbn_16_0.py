# Workflow ID: mgsmbn_16_0
# Benchmark: mgsmbn
# Data Indices: [11]

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

        # PHASE 1: SEMANTIC EXTRACTION & MODELING
        initial_extraction = await self.generate(
            instruction="""Perform a comprehensive semantic extraction of the Bengali word problem. Identify and structure:
            1. All named entities (people, objects, categories) with roles
            2. All numerical values with explicit units (টাকা, ঘণ্টা, জিনিস, etc.)
            3. Temporal or causal sequences (what happens first, next, finally)
            4. Comparison operators (বেশি, কম, সমান) and their targets
            5. The ultimate unknown (what is being asked)
            6. Any percentages, fractions, or ratios and their base values
            7. Implicit constraints (non-negative, integer-only, real-world plausibility)
            Format as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL INTERPRETATION FORK
        interpretation_tasks = [
            self.generate(
                instruction=f"""Interpret the problem assuming all percentage changes are MULTIPLICATIVE (e.g., 2.5% increase = ×1.025).
                Reconstruct the mathematical model using this assumption. Explicitly state:
                - The formula for each step
                - How units propagate
                - Why this interpretation is linguistically justified
                Context: {initial_extraction}""",
                context=initial_extraction
            ),
            self.generate(
                instruction=f"""Interpret the problem assuming all percentage changes are ADDITIVE (e.g., 2.5% increase = +0.025×original).
                Reconstruct the mathematical model using this assumption. Explicitly state:
                - The formula for each step
                - How units propagate
                - Why this interpretation is linguistically justified
                Context: {initial_extraction}""",
                context=initial_extraction
            ),
            self.generate(
                instruction=f"""Validate UNIT CONSISTENCY across all operations. Identify:
                - Where unit conversions are needed (e.g., hours to minutes)
                - Where unit mismatches would cause errors
                - How to resolve ambiguities
                Propose a unit-normalized mathematical model.
                Context: {initial_extraction}""",
                context=initial_extraction
            ),
            self.generate(
                instruction=f"""Validate TEMPORAL SEQUENCE. Reorder operations chronologically if needed.
                Identify hidden steps (e.g., 'after selling, he bought' implies subtraction then addition).
                Reconstruct the model with explicit step ordering.
                Context: {initial_extraction}""",
                context=initial_extraction
            )
        ]

        interpretations = await asyncio.gather(*interpretation_tasks)

        # PHASE 3: ENSEMBLE VALIDATION
        validated_model = await self.ensemble(
            instruction="""Select the most mathematically and linguistically valid interpretation from the four candidates.
            Criteria:
            1. Must preserve unit consistency throughout
            2. Must align with elementary math curriculum (no advanced concepts)
            3. Must avoid negative quantities or fractional people/objects unless explicitly allowed
            4. Must respect chronological order if time-based
            5. Must choose multiplicative vs additive percentage based on Bengali phrasing cues
            Justify your selection with specific references to the problem text.
            Output ONLY the selected model in structured format.""",
            contexts_list=interpretations
        )

        # PHASE 4: SOLUTION PLANNING
        solution_plan = await self.generate(
            instruction=f"""Create a step-by-step solution plan for the validated model. For each step:
            - State the operation (add, subtract, multiply, divide, etc.)
            - Specify inputs and outputs with units
            - Note any intermediate variables
            - Include verification checks (e.g., 'result should be positive')
            Format as numbered steps with clear mathematical notation.
            Context: {validated_model}""",
            context=validated_model
        )

        refined_plan = await self.revise(
            instruction="""Improve the solution plan by:
            1. Adding missing unit conversions
            2. Inserting validation checks after each step
            3. Ensuring chronological alignment
            4. Clarifying ambiguous operations
            5. Adding fallback logic for edge cases (e.g., division by zero)
            Output the final plan in executable pseudocode format.""",
            context=solution_plan
        )

        # PHASE 5: COMPUTATION WITH FEEDBACK LOOP
        answer = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                computation_result = await self.programmer(
                    instruction=f"""Implement the solution plan as Python code. Requirements:
                    1. Use descriptive variable names matching the plan
                    2. Include assertions after each step to validate results
                    3. Handle edge cases with try-except blocks
                    4. Print intermediate results for debugging
                    5. Final answer must be stored in variable 'final_answer'
                    Context: {refined_plan}""",
                    context=refined_plan,
                    max_retries=1
                )
                
                # Extract numerical answer from computation_result
                match = re.search(r'final_answer\s*=\s*([\-0-9\.]+)', computation_result)
                if match:
                    answer = float(match.group(1))
                    break
                else:
                    raise ValueError("Final answer not found in output")
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    break
                refined_plan = await self.revise(
                    instruction=f"""The computation failed with error: {str(e)}
                    Revise the solution plan to fix this issue. Consider:
                    - Adding input validation
                    - Handling zero/edge cases explicitly
                    - Adjusting data types
                    - Simplifying complex operations
                    Output revised plan.""",
                    context=refined_plan
                )

        # PHASE 6: FALLBACK DECOMPOSITION (if computation failed)
        if answer is None:
            subproblems = await self.decompose(
                instruction="""Break the problem into minimal, independent subproblems. For each:
                - Specify exact inputs and expected outputs
                - Note dependencies on other subproblems
                - Isolate ambiguous or complex steps
                Prioritize subproblems that can be solved with basic arithmetic.
                Format as list of dictionaries with 'id', 'description', 'dependencies'.""",
                context=validated_model
            )
            
            # Solve subproblems in dependency order
            subproblem_results = {}
            for sp in subproblems:
                deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
                if all(dep.strip() in subproblem_results for dep in deps if dep.strip()):
                    sub_context = "\n".join([f"{dep}: {subproblem_results[dep]}" for dep in deps if dep.strip()])
                    sub_result = await self.programmer(
                        instruction=f"""Solve this subproblem: {sp['description']}
                        Use these dependencies: {sub_context}
                        Return only the numerical result.""",
                        context=sub_context or "",
                        max_retries=1
                    )
                    # Extract number from sub_result
                    num_match = re.search(r'([\-0-9\.]+)', sub_result)
                    if num_match:
                        subproblem_results[sp['id']] = float(num_match.group(1))
            
            # Combine results (simplified - assumes final subproblem ID is last)
            if subproblem_results:
                answer = list(subproblem_results.values())[-1]

        # PHASE 7: SANITY CHECK
        if answer is not None:
            sanity_check = await self.generate(
                instruction=f"""Sanity check: Does {answer} make sense for this problem?
                Consider:
                1. Magnitude (is it reasonable for the context?)
                2. Units (does it match the expected unit?)
                3. Real-world plausibility (no negative people, etc.)
                4. Alignment with problem constraints
                If any issue, respond with 'FLAGGED: [reason]'. Otherwise, respond 'OK'.""",
                context=""
            )
            
            if "FLAGGED" in sanity_check:
                # Conservative fallback: assume additive percentages and integer constraints
                conservative_model = await self.generate(
                    instruction=f"""Reinterpret the problem conservatively:
                    1. All percentages are additive
                    2. All quantities must be integers
                    3. No negative values allowed
                    4. Round final answer to nearest integer
                    Re-solve using these constraints.
                    Context: {initial_extraction}""",
                    context=initial_extraction
                )
                
                conservative_answer = await self.programmer(
                    instruction=f"""Implement conservative solution. Round final answer to integer.
                    Store in 'final_answer'.
                    Context: {conservative_model}""",
                    context=conservative_model,
                    max_retries=1
                )
                
                match = re.search(r'final_answer\s*=\s*([\-0-9\.]+)', conservative_answer)
                if match:
                    answer = round(float(match.group(1)))

        return str(int(answer)) if answer == int(answer) else str(answer)