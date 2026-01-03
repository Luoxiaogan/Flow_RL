# Workflow ID: mgsmbn_36_0
# Benchmark: mgsmbn
# Data Indices: [185, 197]

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

        # Step 1: Classify problem type and extract key entities
        classification = await self.generate(
            instruction="""Perform deep semantic analysis of this Bengali math problem:
            1. Identify problem category: Sequential, Rate, Proportional, Distribution, Comparison, or Multi-entity.
            2. Extract all named entities (people, objects, places) and their roles.
            3. List all numerical values with their contextual meaning (e.g., '12টি গাড়ি' → quantity=12, unit=গাড়ি).
            4. Identify the unknown being asked for.
            5. Note any implicit constraints (e.g., 'equal share' implies divisibility, 'time' implies positivity).
            6. Flag potential ambiguities in phrasing.
            Output in structured JSON-like format with keys: category, entities, numbers, unknown, constraints, ambiguities.""",
            context=""
        )

        # Step 2: Generate multiple interpretations if ambiguities exist
        ambiguity_check = await self.generate(
            instruction=f"""Based on this classification:
            {classification}
            
            Determine if there are significant semantic ambiguities that could lead to multiple valid interpretations.
            If yes, describe 2-3 plausible interpretations. If no, state 'UNAMBIGUOUS'.
            Focus on mathematical relationships, not linguistic nuances.""",
            context=classification
        )

        # Step 3: Parallel decomposition and interpretation handling
        if "UNAMBIGUOUS" not in ambiguity_check.upper():
            # Fork: Multiple interpretations
            interpretations = await asyncio.gather(
                self.generate(instruction=f"Interpretation 1: {ambiguity_check.split('.')[0] if '.' in ambiguity_check else ambiguity_check}", context=""),
                self.generate(instruction=f"Interpretation 2: Most mathematically conservative reading", context=""),
                self.generate(instruction=f"Interpretation 3: Contextually most plausible reading based on {classification}", context="")
            )
            
            # Decompose each interpretation
            decompositions = await asyncio.gather(
                *[self.decompose(
                    instruction=f"""Decompose this interpretation into atomic, dependency-aware subproblems:
                    - Each subproblem must be solvable independently given its dependencies
                    - Tag each with expected units and mathematical operation type
                    - Order by dependency (prerequisites first)
                    - Include validation checks (e.g., 'result must be positive integer')""",
                    context=interp
                ) for interp in interpretations]
            )
        else:
            # Single decomposition path
            decompositions = [await self.decompose(
                instruction=f"""Decompose this unambiguous problem into atomic, dependency-aware subproblems:
                - Each subproblem must be solvable independently given its dependencies
                - Tag each with expected units and mathematical operation type
                - Order by dependency (prerequisites first)
                - Include validation checks (e.g., 'result must be positive integer')
                - Cross-reference with classification: {classification}""",
                context=""
            )]

        # Step 4: Solve each decomposition path in parallel
        solution_attempts = []
        for i, decomp in enumerate(decompositions):
            try:
                # Sequentially solve subproblems respecting dependencies
                subproblem_results = {}
                for sub in decomp:
                    # Build context from dependencies
                    dep_context = "\n".join([f"Subproblem {dep}: {subproblem_results.get(dep, 'PENDING')}" 
                                           for dep in sub.get('dependencies', '').split(',') if dep.strip()])
                    
                    # Generate code with explicit instructions
                    code_instruction = f"""Solve this subproblem using Python:
                    Description: {sub['description']}
                    Dependencies: {dep_context}
                    Expected units: {sub.get('units', 'N/A')}
                    Validation constraints: {sub.get('validation', 'None')}
                    Classification context: {classification}
                    
                    Write code that:
                    1. Uses only basic arithmetic and math operations
                    2. Explicitly tracks units in variable names (e.g., cost_taka, time_hours)
                    3. Validates result against constraints
                    4. Returns ONLY the numerical result as a float or int
                    5. If validation fails, raise AssertionError with reason"""
                    
                    result = await self.programmer(
                        instruction=code_instruction,
                        context=dep_context,
                        max_retries=3
                    )
                    subproblem_results[sub['id']] = result
                
                # Extract final answer from last subproblem (assuming DAG ends with answer)
                final_sub = decomp[-1] if decomp else {}
                final_id = final_sub.get('id', list(subproblem_results.keys())[-1] if subproblem_results else "")
                solution = subproblem_results.get(final_id, "ERROR: No final subproblem")
                solution_attempts.append(f"Interpretation {i+1}: {solution}")
            except Exception as e:
                solution_attempts.append(f"Interpretation {i+1}: FAILED - {str(e)}")

        # Step 5: Ensemble best solution with validation
        final_answer = await self.ensemble(
            instruction=f"""Select the best numerical answer from these attempts:
            {solution_attempts}
            
            Selection criteria:
            1. Mathematical consistency with original problem
            2. Adherence to constraints from classification: {classification}
            3. Unit correctness (e.g., no fractional people if context implies whole numbers)
            4. Plausibility (e.g., positive values for counts, reasonable magnitudes)
            5. If all fail, choose the one closest to satisfying constraints
            
            Return ONLY the numerical value. No explanations, units, or text.""",
            contexts_list=solution_attempts
        )

        # Step 6: Final extraction and sanitization
        sanitized = await self.summarize(
            instruction="""Extract ONLY the numerical answer from the following text.
            Remove any units, explanations, or non-numeric characters.
            If multiple numbers, select the one that directly answers the main question.
            Return as plain number (int or float).""",
            context=final_answer
        )

        # Step 7: Validate and revise if necessary (spiral refinement)
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Validate this answer against original problem:
                Answer: {sanitized}
                Problem: {self.problem_text}
                Classification: {classification}
                
                Check:
                1. Does it answer the exact question asked?
                2. Are units consistent? (e.g., if problem asks for টাকা, answer shouldn't be in ঘণ্টা)
                3. Does it satisfy all implicit constraints? (e.g., whole numbers for countable items)
                4. Is magnitude reasonable? (e.g., not 10^9 for a classroom problem)
                
                If valid, return 'VALID'. If invalid, return 'INVALID: [reason]'""",
                context=sanitized
            )
            
            if "VALID" in validation:
                break
            else:
                sanitized = await self.revise(
                    instruction=f"""Revise the answer based on validation feedback:
                    Current answer: {sanitized}
                    Validation feedback: {validation}
                    Problem context: {classification}
                    
                    Adjust by:
                    1. Correcting unit mismatches
                    2. Enforcing constraint violations (e.g., round to integer if needed)
                    3. Re-evaluating mathematical relationships
                    4. Returning ONLY the revised numerical value""",
                    context=sanitized
                )
        else:
            # Final fallback: extract first number from sanitized
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", sanitized)
            sanitized = numbers[0] if numbers else "0"

        return sanitized