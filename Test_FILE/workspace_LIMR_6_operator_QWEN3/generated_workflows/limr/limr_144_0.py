# Workflow ID: limr_144_0
# Benchmark: limr
# Data Indices: [205, 89]

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

        # STEP 1: PARALLEL PROBLEM CLASSIFICATION
        classification_attempts = await asyncio.gather(
            self.generate(
                instruction="""Analyze the problem and classify it with extreme precision. Consider:
                - Primary domain: Geometry, Number Theory, Algebra, Combinatorics, Probability, Optimization, Sequences
                - Required techniques: Coordinate geometry, modular arithmetic, polynomial manipulation, counting principles, calculus, etc.
                - Key objects: Vectors, angles, equations, sequences, probabilities, inequalities
                - Expected answer format: Integer between 000-999, possibly derived from intermediate steps
                - Potential pitfalls: Sign errors, quadrant ambiguities, off-by-one errors, implicit constraints
                Output a structured JSON with keys: "domain", "techniques", "objects", "format", "pitfalls".""",
                context=""
            ),
            self.generate(
                instruction="""Independently classify this problem by focusing on solution strategy:
                - Is this primarily a computational problem or a proof/derivation problem?
                - What mathematical transformations are likely needed? (e.g., coordinate change, substitution, symmetry exploitation)
                - What level of abstraction is required? (concrete calculation vs. general principle)
                - Are there multiple valid approaches? If so, list them.
                - What is the most efficient path to solution?
                Output as JSON with keys: "strategy_type", "transformations", "abstraction_level", "approaches", "efficiency".""",
                context=""
            ),
            self.generate(
                instruction="""Classify by mathematical structure:
                - What are the governing equations or relationships?
                - What are the degrees of freedom and constraints?
                - Is this problem underdetermined, overdetermined, or well-posed?
                - What invariants or symmetries exist?
                - What boundary conditions or special cases apply?
                Output as JSON with keys: "equations", "constraints", "determination", "invariants", "boundaries".""",
                context=""
            )
        )

        # STEP 2: ENSEMBLE CLASSIFICATIONS INTO UNIFIED VIEW
        unified_classification = await self.ensemble(
            instruction="""Synthesize these three independent classifications into a single, coherent problem analysis. Resolve contradictions by prioritizing specificity and mathematical rigor. Output must be a comprehensive JSON with all keys from all classifications, plus:
            - "confidence_score": 0-1 based on consensus strength
            - "recommended_approach": The single most promising solution path
            - "validation_strategy": How to verify the solution (algebraic, numeric, geometric, etc.)
            Ensure no key is missing. If classifications conflict, note the conflict and choose the most mathematically sound option.""",
            contexts_list=classification_attempts
        )

        # STEP 3: DYNAMIC DECOMPOSITION BASED ON CLASSIFICATION
        decomposition_plan = await self.generate(
            instruction=f"""Based on this unified classification:
            {unified_classification}
            
            Generate a detailed decomposition strategy. Specify:
            - How many subproblems are needed?
            - What is the dependency graph between them?
            - What mathematical tools are required for each?
            - What intermediate outputs must be validated?
            - What fallback strategies exist if a subproblem fails?
            Output as a bulleted list of decomposition instructions.""",
            context=unified_classification
        )

        subproblems = await self.decompose(
            instruction=f"""Decompose the problem using this strategy:
            {decomposition_plan}
            
            Each subproblem must be:
            - Mathematically self-contained (given dependencies)
            - Solvable with specified tools
            - Verifiable against original constraints
            - Tagged with expected output format (equation, number, vector, etc.)
            Return list of subproblems with IDs, descriptions, and dependencies.""",
            context=decomposition_plan
        )

        # STEP 4: PARALLEL SUBPROBLEM SOLVING
        async def solve_subproblem(subproblem):
            sub_id = subproblem['id']
            description = subproblem['description']
            deps = subproblem.get('dependencies', '')
            
            # Generate solution approach
            approach = await self.generate(
                instruction=f"""For subproblem {sub_id}: {description}
                Dependencies: {deps}
                Generate a step-by-step solution plan. Include:
                - Required formulas or theorems
                - Variable definitions
                - Expected intermediate results
                - Potential error points
                - Validation method for this subproblem""",
                context=unified_classification
            )
            
            # Attempt computational solution
            try:
                result = await self.programmer(
                    instruction=f"""Implement and execute the solution for subproblem {sub_id}:
                    {description}
                    Using approach: {approach}
                    Return result in specified format. Include all code and output.""",
                    context=approach,
                    max_retries=3
                )
            except Exception:
                # Fallback: Generate symbolic solution
                result = await self.generate(
                    instruction=f"""Subproblem {sub_id} failed computationally. Derive solution symbolically:
                    {description}
                    Show all algebraic steps. Box final answer.""",
                    context=approach
                )
            
            return {
                'id': sub_id,
                'description': description,
                'result': result,
                'approach': approach
            }

        # Solve all subproblems in parallel
        solved_subproblems = await asyncio.gather(
            *[solve_subproblem(sp) for sp in subproblems]
        )

        # STEP 5: INTEGRATE AND VALIDATE
        integration_context = "\n\n".join([
            f"Subproblem {sp['id']}: {sp['description']}\nResult: {sp['result']}\nApproach: {sp['approach']}"
            for sp in solved_subproblems
        ])

        integrated_solution = await self.generate(
            instruction=f"""Integrate all subproblem results into a complete solution:
            {integration_context}
            
            Steps:
            1. Combine results according to dependency graph
            2. Resolve any inconsistencies
            3. Derive final answer (integer 000-999)
            4. Show complete logical flow from problem to answer
            5. Box final answer as ###ANSWER: <integer>###""",
            context=integration_context
        )

        # STEP 6: ADVERSARIAL VALIDATION
        validators = await asyncio.gather(
            self.generate(
                instruction=f"""Validate algebraically: Check all equations, substitutions, and derivations in:
                {integrated_solution}
                Flag any inconsistencies, sign errors, or logical gaps. Output 'VALID' or 'INVALID: <reason>'""",
                context=integrated_solution
            ),
            self.generate(
                instruction=f"""Validate numerically: Plug final answer back into original problem constraints. Does it satisfy all conditions? Output 'VALID' or 'INVALID: <reason>'""",
                context=integrated_solution
            ),
            self.generate(
                instruction=f"""Validate dimensionally/structurally: Do units, magnitudes, and mathematical types make sense? (e.g., vector vs scalar, angle vs length) Output 'VALID' or 'INVALID: <reason>'""",
                context=integrated_solution
            )
        )

        validation_result = await self.ensemble(
            instruction="""Aggregate validation results. If all say 'VALID', output the original solution. If any say 'INVALID', trigger revision with specific error feedback. Output format: either the original solution (if valid) or 'REVISION_NEEDED: <consolidated_feedback>'""",
            contexts_list=validators
        )

        # STEP 7: ITERATIVE REFINEMENT (max 2 iterations)
        current_solution = integrated_solution
        for iteration in range(2):
            if "REVISION_NEEDED" not in validation_result:
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise solution based on validation feedback:
                {validation_result}
                Fix all identified errors. Maintain original structure but correct flaws. Re-derive if necessary. Box final answer as ###ANSWER: <integer>###""",
                context=current_solution
            )
            
            # Re-validate
            new_validators = await asyncio.gather(
                self.generate(instruction="Validate algebraically...", context=current_solution),
                self.generate(instruction="Validate numerically...", context=current_solution),
                self.generate(instruction="Validate dimensionally...", context=current_solution)
            )
            validation_result = await self.ensemble(
                instruction="Aggregate validation results...",
                contexts_list=new_validators
            )

        # STEP 8: META-REFLECTION AND FINAL OUTPUT
        trust_report = await self.generate(
            instruction=f"""Generate a trust report for this solution:
            - Confidence level (0-10): Based on validation strength and consensus
            - Key assumptions made
            - Most fragile part of solution
            - Alternative approaches considered
            - Why this answer is likely correct
            Format as JSON.""",
            context=current_solution
        )

        final_output = await self.ensemble(
            instruction="""Combine the solution and trust report. If confidence is high (>=8), output only the answer in format ###ANSWER: <integer>###. If confidence is medium (5-7), output answer with brief caveat. If low (<5), output 'UNCERTAIN' and request human review.""",
            contexts_list=[current_solution, trust_report]
        )

        # Extract final answer
        if "###ANSWER:" in final_output:
            import re
            match = re.search(r"###ANSWER:\s*(\d{1,3})###", final_output)
            if match:
                answer = match.group(1).zfill(3)  # Ensure 3-digit format
                return answer
        
        # Fallback: extract any 3-digit number
        numbers = re.findall(r"\b\d{1,3}\b", final_output)
        if numbers:
            return numbers[-1].zfill(3)
        
        return "000"  # Ultimate fallback