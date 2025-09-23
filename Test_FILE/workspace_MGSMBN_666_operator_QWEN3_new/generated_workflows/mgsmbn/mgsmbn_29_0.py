# Workflow ID: mgsmbn_29_0
# Benchmark: mgsmbn
# Data Indices: [193, 145]

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

        # STEP 1: PARALLEL PROBLEM INTERPRETATION & CLASSIFICATION
        # Generate multiple foundational interpretations to avoid early commitment bias
        initial_interpretations = await asyncio.gather(
            self.generate(
                instruction="""Perform deep linguistic and mathematical interpretation of the Bengali word problem. 
                Extract:
                - All numerical values and their contextual meaning (e.g., '80' = total voters)
                - All entities (people, objects) and their relationships
                - Verbs indicating operations (add, subtract, share, compare)
                - Units of measurement (টাকা, ঘণ্টা, জিনিস, etc.)
                - Implicit constraints (e.g., 'people' implies integer answer)
                Structure output as clear bullet points with labeled categories.""",
                context=""
            ),
            self.generate(
                instruction="""Classify this problem into one primary type and note supporting evidence:
                Types: Sequential, Rate, Proportional, Distribution, Comparison, Multi-entity.
                Also identify:
                - Required mathematical operations
                - Potential hidden steps
                - Answer format expectations (integer, decimal, unit)
                - Any ambiguous phrasing needing clarification
                Provide structured classification with justification.""",
                context=""
            )
        )

        # Synthesize interpretations into unified problem understanding
        problem_understanding = await self.ensemble(
            instruction="""Synthesize the linguistic extraction and problem classification into a single coherent problem model.
            Prioritize:
            1. Mathematical structure over literal translation
            2. Explicit constraints from context
            3. Resolution of any conflicting interpretations
            Output must include:
            - Problem type
            - Key entities and values
            - Required operations
            - Expected answer format
            - Any assumptions made""",
            contexts_list=initial_interpretations
        )

        # STEP 2: HIERARCHICAL DECOMPOSITION WITH DYNAMIC INSTRUCTIONS
        decomposition_instruction = f"""Decompose this Bengali math problem into minimal, solvable subproblems with explicit dependencies.
        Use the following context: {problem_understanding}
        
        Guidelines:
        - Each subproblem must be computationally or logically self-contained
        - Specify dependencies using subproblem IDs (e.g., "2" depends on "1")
        - Include unit tracking for each subproblem
        - Flag any subproblem requiring assumptions
        - For proportional problems: identify whole, part, ratio
        - For multi-entity: create entity-state tracking
        - For sequential: maintain chronological order
        
        Output as list of dictionaries with keys: id, description, dependencies"""
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # STEP 3: PARALLEL SUBPROBLEM SOLVING WITH VALIDATION
        async def solve_subproblem(subproblem):
            # Generate initial solution attempt
            solution_attempt = await self.generate(
                instruction=f"""Solve this subproblem: {subproblem['description']}
                Context: {problem_understanding}
                Requirements:
                - Show step-by-step reasoning
                - Track units explicitly
                - State any assumptions
                - Format final answer clearly""",
                context=""
            )
            
            # Validate and revise if necessary
            validated_solution = await self.revise(
                instruction="""Critically validate this solution:
                - Check arithmetic accuracy
                - Verify unit consistency
                - Ensure real-world plausibility (no negative books, fractional people unless specified)
                - Confirm alignment with original problem constraints
                If errors found, correct them and explain fixes.
                If ambiguous, state assumptions clearly.""",
                context=solution_attempt
            )
            
            return {
                "id": subproblem["id"],
                "solution": validated_solution,
                "original": subproblem
            }

        # Solve subproblems in topological order (respecting dependencies)
        solved_subproblems = {}
        remaining_subproblems = {sp["id"]: sp for sp in subproblems}
        
        while remaining_subproblems:
            # Find subproblems whose dependencies are satisfied
            ready_subproblems = []
            for sp_id, sp in remaining_subproblems.items():
                deps = sp.get("dependencies", "").split(",") if sp.get("dependencies") else []
                if all(dep.strip() in solved_subproblems for dep in deps if dep.strip()):
                    ready_subproblems.append(sp)
            
            if not ready_subproblems:
                # Circular dependency or missing info - break with error
                break
                
            # Solve ready subproblems in parallel
            solutions = await asyncio.gather(
                *[solve_subproblem(sp) for sp in ready_subproblems]
            )
            
            # Store solutions
            for solution in solutions:
                solved_subproblems[solution["id"]] = solution
                del remaining_subproblems[solution["id"]]

        # STEP 4: SYNTHESIZE FINAL ANSWER
        synthesis_context = "\n\n".join([
            f"Subproblem {sol['id']}: {sol['solution']}" 
            for sol in solved_subproblems.values()
        ])
        
        final_answer_draft = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into final answer:
            {synthesis_context}
            
            Requirements:
            - Combine results according to problem logic
            - Perform final calculation if needed
            - Ensure unit consistency
            - Verify against original problem constraints
            - Output ONLY the numerical answer (integer or decimal) with no explanation""",
            context=problem_understanding
        )

        # STEP 5: MULTI-PERSPECTIVE VALIDATION & ENSEMBLE
        validation_perspectives = await asyncio.gather(
            self.generate(
                instruction=f"""Validate final answer: {final_answer_draft}
                Check:
                1. Does it match dimensional analysis? (e.g., books should be integer)
                2. Does it satisfy all original constraints?
                3. Is it within reasonable bounds? (e.g., can't have more books than exist)
                4. Cross-verify with alternative calculation path if possible
                Output: "VALID" or "INVALID: [reasons]" """,
                context=problem_understanding
            ),
            self.programmer(
                instruction=f"""Write Python code to verify the final answer: {final_answer_draft}
                Based on original problem and subproblem solutions.
                Code must:
                - Recalculate from original values
                - Include assertions for constraints
                - Output only the verified numerical result
                If verification fails, output error message.""",
                context=synthesis_context
            )
        )

        # Ensemble final decision
        final_answer = await self.ensemble(
            instruction="""Select the most reliable answer based on:
            1. Numerical accuracy (prioritize programmer verification)
            2. Contextual plausibility (integer when required, positive values)
            3. Consistency with problem constraints
            If conflict, prefer programmer result unless it violates real-world constraints.
            Output ONLY the final numerical answer (integer or decimal) with no explanation.""",
            contexts_list=[final_answer_draft] + validation_perspectives
        )

        # Clean and return final answer
        # Extract only numerical value (handles cases where text might be included)
        import re
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return original draft if parsing fails
            match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer_draft)
            return match.group(0) if match else "0"