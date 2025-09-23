# Workflow ID: mgsmbn_44_0
# Benchmark: mgsmbn
# Data Indices: [142, 151]

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

        # STEP 1: SEMANTIC EXTRACTION & ANCHORING
        # Extract and label all numerical entities with semantic roles
        semantic_extraction = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and extract every numerical value with its semantic context. For each number, specify:
            - The exact value
            - The entity it describes (e.g., cost, quantity, rate, time)
            - The unit of measurement (টাকা, ঘণ্টা, গ্লাস, etc.)
            - The relationship to other entities (e.g., 'per gallon', 'monthly', 'total')
            - Whether it's a given, intermediate, or target value
            Format as a structured JSON-like list with clear labels. Preserve Bengali terms where meaning is context-dependent.""",
            context=""
        )

        # STEP 2: HIERARCHICAL DECOMPOSITION
        # Break problem into logical, dependent subproblems
        subproblems = await self.decompose(
            instruction="""Decompose this math word problem into minimal, logically independent subproblems. Each subproblem should:
            - Represent one atomic calculation or inference step
            - Specify input dependencies (which other subproblems must be solved first)
            - Identify required operations (addition, percentage, unit conversion, etc.)
            - Flag any ambiguous interpretations that need resolution
            - Prioritize subproblems that resolve unit consistency or entity relationships first
            Return as a list of dictionaries with 'id', 'description', and 'dependencies'.""",
            context=semantic_extraction
        )

        # STEP 3: PARALLEL SOLUTION GENERATION (ADVERSARIAL BRANCHING)
        # Generate multiple solution approaches for ambiguous or critical subproblems
        solution_attempts = []
        
        # Identify ambiguous or high-impact subproblems for parallel solving
        ambiguous_subproblems = [
            sp for sp in subproblems 
            if "ambiguous" in sp['description'].lower() or 
               "interpret" in sp['description'].lower() or
               "assume" in sp['description'].lower()
        ]
        
        if not ambiguous_subproblems:
            # If no explicit ambiguity, target the final calculation subproblem
            final_subproblem = max(subproblems, key=lambda x: len(x.get('dependencies', '').split(',')) if x.get('dependencies') else 0)
            ambiguous_subproblems = [final_subproblem]

        # Generate 3 distinct solution strategies for each ambiguous subproblem
        for subproblem in ambiguous_subproblems[:2]:  # Limit to top 2 most complex
            strategies = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve subproblem: {subproblem['description']}
                    Strategy 1: Assume literal interpretation of all terms. Use basic arithmetic without advanced assumptions. Prioritize direct calculations from given numbers.""",
                    context=semantic_extraction
                ),
                self.generate(
                    instruction=f"""Solve subproblem: {subproblem['description']}
                    Strategy 2: Consider contextual and real-world implications. Apply proportional reasoning or unit conversions where implied but not stated. Assume standard practices (e.g., simple interest unless specified).""",
                    context=semantic_extraction
                ),
                self.generate(
                    instruction=f"""Solve subproblem: {subproblem['description']}
                    Strategy 3: Mathematical formalism approach. Convert to algebraic equations. Define variables for unknowns. Solve symbolically before substituting numbers. Check for multiple solutions or constraints.""",
                    context=semantic_extraction
                )
            )
            solution_attempts.extend(strategies)

        # STEP 4: PROGRAMMATIC VALIDATION OF KEY CALCULATIONS
        # Convert best candidate solutions to executable code for verification
        code_solutions = []
        for i, attempt in enumerate(solution_attempts[:3]):  # Limit to 3 for efficiency
            try:
                code_solution = await self.programmer(
                    instruction=f"""Convert this mathematical reasoning into executable Python code:
                    - Define all variables with clear names
                    - Include unit tracking in comments
                    - Add assertions for sanity checks (e.g., non-negative values, reasonable ranges)
                    - Output only the final numerical answer
                    - Handle edge cases mentioned in the reasoning
                    The code must be self-contained and mathematically precise.""",
                    context=attempt,
                    max_retries=2
                )
                code_solutions.append(code_solution)
            except Exception:
                # Fallback: keep the textual solution if code generation fails
                code_solutions.append(attempt)

        # STEP 5: ENSEMBLE SYNTHESIS WITH VALIDATION CRITERIA
        # Synthesize best answer from parallel attempts with validation
        synthesized_answer = await self.ensemble(
            instruction="""Evaluate all solution attempts and select the most correct answer based on:
            1. MATHEMATICAL CORRECTNESS: Does the calculation follow from the premises without error?
            2. UNIT CONSISTENCY: Are units tracked properly throughout? Do final units match expected answer type?
            3. CONTEXTUAL FIT: Does the solution respect real-world constraints (no negative people, fractional items only if allowed)?
            4. NARRATIVE ALIGNMENT: Does the solution follow the chronological or causal flow described in the problem?
            5. ROBUSTNESS: Does the solution handle edge cases or alternative interpretations gracefully?
            Return ONLY the final numerical answer as a single number, with brief justification.""",
            contexts_list=code_solutions
        )

        # STEP 6: ADVERSARIAL REVISION LOOP (AT MOST 2 ITERATIONS)
        # Verify answer by back-calculation and revise if inconsistency found
        current_answer = synthesized_answer
        for iteration in range(2):
            verification = await self.generate(
                instruction=f"""Perform adversarial verification on this answer: {current_answer}
                - Work backwards: Assume this answer is correct, then recalculate all given values from it.
                - Check if recalculated values match original problem statements.
                - Identify any inconsistencies in units, magnitudes, or logical flow.
                - If inconsistency found, propose corrected calculation path.
                - If consistent, confirm 'VERIFIED'.""",
                context=f"Original Analysis: {semantic_extraction}\n\nSolution Attempts: {str(solution_attempts[:3])}"
            )
            
            if "VERIFIED" in verification or "verified" in verification or iteration == 1:
                break
            else:
                # Revise based on verification feedback
                current_answer = await self.revise(
                    instruction=f"""Revise the solution based on verification feedback: {verification}
                    - Correct any mathematical errors
                    - Adjust for unit inconsistencies
                    - Reinterpret ambiguous phrases based on verification insights
                    - Maintain focus on the original question
                    Output ONLY the revised numerical answer.""",
                    context=current_answer
                )

        # STEP 7: FINAL EXTRACTION AND CLEANUP
        # Ensure output is a clean numerical value
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the text below. 
            - Remove any units, explanations, or qualifiers
            - If answer is decimal, preserve exact precision
            - If multiple numbers present, select the one that directly answers the question
            - Output must be a single number (integer or decimal) with no additional text.""",
            context=current_answer
        )

        return final_answer.strip()