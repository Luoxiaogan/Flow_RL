# Workflow ID: mgsmbn_12_0
# Benchmark: mgsmbn
# Data Indices: [69]

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
        from typing import Dict, List, Any, Set

        # STEP 1: Problem Classification & Entity Extraction (Parallel Perspectives)
        classification_task = self.generate(
            instruction="""Perform comprehensive problem analysis:
            1. CLASSIFY problem type: Choose primary category from [Sequential, Rate, Proportional, Distribution, Comparison, Multi-entity]. 
            2. EXTRACT all numerical values with their semantic roles (e.g., '10 পাউন্ড' → quantity=10, unit='পাউন্ড', refers_to='adult_dinosaur_portion').
            3. IDENTIFY key entities: People, objects, groups with their descriptors.
            4. DETECT mathematical relationships: Ratios, fractions, comparisons, operations implied by verbs.
            5. FLAG ambiguities: Pronoun references, omitted quantities, cultural assumptions.
            Output in structured JSON-like format even if approximate.""",
            context=""
        )

        constraint_task = self.generate(
            instruction="""Identify implicit constraints and real-world boundaries:
            - Physical impossibilities (negative quantities, fractional people)
            - Unit consistency requirements
            - Ceiling/floor conditions (e.g., 'how many buses' implies integer rounding up)
            - Temporal or logical order dependencies
            - Cultural or contextual assumptions specific to Bengali context
            List each constraint explicitly with justification from problem text.""",
            context=""
        )

        # Execute in parallel
        classification_result, constraint_result = await asyncio.gather(classification_task, constraint_task)

        # STEP 2: Hierarchical Decomposition with Dependency Awareness
        decomposition = await self.decompose(
            instruction=f"""Decompose into minimal computational subproblems with explicit dependencies:
            Using classification: {classification_result}
            And constraints: {constraint_result}
            
            For each subproblem:
            - Define input variables and their sources
            - Specify exact mathematical operation
            - State output variable and its purpose
            - List dependency IDs (comma-separated) of prerequisite subproblems
            - Include unit handling instructions
            
            Prioritize atomic operations. No subproblem should require more than one arithmetic operation or unit conversion.""",
            context=f"{classification_result}\n\n{constraint_result}"
        )

        # STEP 3: Build Execution Graph and Schedule
        subproblem_results: Dict[str, Any] = {}
        pending_subproblems: List[Dict[str, str]] = decomposition.copy()
        
        # Iterative execution respecting dependencies
        iteration = 0
        max_iterations = len(decomposition) + 2  # Safety limit
        
        while pending_subproblems and iteration < max_iterations:
            iteration += 1
            executable_now = []
            remaining = []
            
            for sp in pending_subproblems:
                deps = sp.get('dependencies', '').strip()
                if not deps:  # No dependencies
                    executable_now.append(sp)
                else:
                    dep_ids = [d.strip() for d in deps.split(',') if d.strip()]
                    if all(dep_id in subproblem_results for dep_id in dep_ids):
                        executable_now.append(sp)
                    else:
                        remaining.append(sp)
            
            if not executable_now:
                # Deadlock or missing deps - break to avoid infinite loop
                break
                
            # Execute executable subproblems in parallel
            async def solve_subproblem(sp: Dict[str, str]) -> tuple:
                try:
                    # Inject known results into context
                    dep_context = "\n".join([f"{k}: {v}" for k, v in subproblem_results.items()])
                    full_context = f"Dependencies resolved:\n{dep_context}\n\nSubproblem: {sp['description']}"
                    
                    solution = await self.programmer(
                        instruction=f"""Solve this atomic subproblem with validation:
                        Description: {sp['description']}
                        Required operation: Extract exact arithmetic from description.
                        Validate: Check against constraints: {constraint_result}
                        Verify: Ensure output is physically plausible (no negatives, correct units).
                        If validation fails, auto-correct (e.g., apply ceiling for people, floor for resources).
                        Return ONLY the numerical result with unit if applicable.""",
                        context=full_context,
                        max_retries=3
                    )
                    
                    # Extract number from solution string
                    number_match = re.search(r'[-+]?\d*\.\d+|\d+', solution)
                    if number_match:
                        return sp['id'], float(number_match.group())
                    else:
                        return sp['id'], f"PARSING_ERROR: {solution}"
                except Exception as e:
                    return sp['id'], f"EXECUTION_ERROR: {str(e)}"
            
            # Run all executable subproblems concurrently
            results = await asyncio.gather(*[solve_subproblem(sp) for sp in executable_now])
            for sp_id, result in results:
                subproblem_results[sp_id] = result
            
            pending_subproblems = remaining

        # STEP 4: Meta-Validation and Error Recovery
        validation = await self.generate(
            instruction=f"""Critique the solution process:
            Subproblem results: {subproblem_results}
            Original problem: {self.problem_text}
            
            Check for:
            1. Consistency: Do results align with extracted constraints?
            2. Completeness: Were all subproblems resolved?
            3. Plausibility: Is final magnitude reasonable? (e.g., not 10000 for picnic salad)
            4. Unit integrity: Were units preserved and converted correctly?
            
            If any issue found, specify which subproblem ID(s) need revision and why.""",
            context=str(subproblem_results)
        )

        # If validation flags issues, trigger targeted revision
        if "issue" in validation.lower() or "error" in validation.lower() or "revise" in validation.lower():
            # Extract problematic subproblem IDs
            mentioned_ids = set()
            for sp in decomposition:
                if sp['id'] in validation:
                    mentioned_ids.add(sp['id'])
            
            # Re-solve problematic subproblems with enhanced context
            for sp_id in mentioned_ids:
                sp = next((s for s in decomposition if s['id'] == sp_id), None)
                if sp:
                    enhanced_context = f"VALIDATION FEEDBACK: {validation}\n\nPREVIOUS ATTEMPT: {subproblem_results.get(sp_id, 'None')}\n\nCONSTRAINTS: {constraint_result}"
                    revised_solution = await self.programmer(
                        instruction=f"""Revise this subproblem with strict validation:
                        Original description: {sp['description']}
                        Previous result: {subproblem_results.get(sp_id, 'None')}
                        Validation feedback: {validation}
                        Constraints: {constraint_result}
                        Apply necessary corrections (rounding, unit conversion, sign correction).
                        Return ONLY the corrected numerical value.""",
                        context=enhanced_context,
                        max_retries=2
                    )
                    number_match = re.search(r'[-+]?\d*\.\d+|\d+', revised_solution)
                    if number_match:
                        subproblem_results[sp_id] = float(number_match.group())

        # STEP 5: Final Answer Synthesis
        # Identify which subproblem contains the final answer (usually last in dependency chain)
        final_candidates = []
        for sp in decomposition:
            # Subproblems with no dependents are potential final answers
            is_final = not any(sp['id'] in (s.get('dependencies', '') or '') for s in decomposition)
            if is_final:
                final_candidates.append(subproblem_results.get(sp['id'], "MISSING"))
        
        if not final_candidates:
            final_candidates = list(subproblem_results.values())  # Fallback: use all results

        # Use Ensemble to extract and unify final numerical answer
        final_answer = await self.ensemble(
            instruction="""Extract the single numerical answer that solves the original problem:
            - From multiple candidate values, select the one that directly answers the question.
            - Ignore intermediate values, units, or explanatory text.
            - If candidates conflict, choose the one consistent with constraints and problem context.
            - Return ONLY the number (integer or decimal) with no additional text.""",
            contexts_list=[str(c) for c in final_candidates]
        )

        # STEP 6: Sanity Check and Fallback
        sanity_check = await self.generate(
            instruction=f"""Final validation:
            Proposed answer: {final_answer}
            Original problem: {self.problem_text}
            Constraints: {constraint_result}
            
            Answer 'VALID' if:
            - Number is non-negative (unless context allows negatives)
            - Magnitude is plausible (e.g., not millions for picnic food)
            - Matches expected unit scale (pounds, hours, etc.)
            Otherwise, answer 'INVALID' and briefly state why.""",
            context=str(final_answer)
        )

        if "invalid" in sanity_check.lower():
            # Fallback: Three independent solution attempts
            fallback_strategies = [
                "Solve algebraically: Define variables, write equations, solve symbolically.",
                "Solve step-by-step arithmetically: Break into smallest operations, show all steps.",
                "Solve by unit tracking: Follow units through each operation, ensure dimensional consistency."
            ]
            
            fallback_attempts = await asyncio.gather(*[
                self.generate(
                    instruction=f"{strategy}\n\nReturn ONLY the final numerical answer.",
                    context=""
                ) for strategy in fallback_strategies
            ])
            
            # Extract numbers from fallback attempts
            extracted_numbers = []
            for attempt in fallback_attempts:
                num_match = re.search(r'[-+]?\d*\.\d+|\d+', attempt)
                if num_match:
                    extracted_numbers.append(num_match.group())
                else:
                    extracted_numbers.append(attempt)  # Keep as string if no number found
            
            # Vote on most plausible answer
            final_answer = await self.ensemble(
                instruction="""Select the most plausible final answer:
                - Prefer answers that are integers if context implies whole units (people, items).
                - Prefer positive values unless context allows negatives.
                - Eliminate outliers that differ by orders of magnitude.
                - Return ONLY the selected number.""",
                contexts_list=extracted_numbers
            )

        # Ensure output is clean numerical string
        clean_match = re.search(r'[-+]?\d*\.\d+|\d+', str(final_answer))
        if clean_match:
            return clean_match.group()
        else:
            return "0"  # Ultimate fallback