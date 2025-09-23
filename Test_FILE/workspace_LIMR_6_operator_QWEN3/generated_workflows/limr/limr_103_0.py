# Workflow ID: limr_103_0
# Benchmark: limr
# Data Indices: [169, 115]

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
        classification_instructions = [
            """Analyze this problem from an ALGEBRAIC/ANALYTIC perspective:
            - Identify all equations, functions, variables, and unknowns
            - Determine if polynomial, functional, or transcendental methods apply
            - Note any symmetries, substitutions, or transformations that simplify the problem
            - Suggest algebraic theorems or identities that might be relevant
            Structure your response with clear sections: Variables, Equations, Potential Methods, Key Insights.""",
            
            """Analyze this problem from a GEOMETRIC/SPATIAL perspective:
            - Identify all geometric objects, dimensions, coordinates, and relationships
            - Determine if coordinate geometry, vector methods, or synthetic geometry applies
            - Note any symmetries, invariants, or transformations (rotation, reflection, scaling)
            - Suggest relevant geometric theorems or formulas
            Structure your response with clear sections: Objects, Relationships, Potential Methods, Key Insights.""",
            
            """Analyze this problem from a COMBINATORIAL/PROBABILISTIC perspective:
            - Identify all discrete elements, counting scenarios, or probabilistic events
            - Determine if permutations, combinations, recursion, or probabilistic independence applies
            - Note any symmetries, overcounting risks, or complementary counting opportunities
            - Suggest relevant combinatorial identities or probability rules
            Structure your response with clear sections: Elements, Scenarios, Potential Methods, Key Insights."""
        ]

        # Generate parallel analyses
        raw_analyses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in classification_instructions]
        )

        # Revise each analysis for depth and precision
        refined_analyses = await asyncio.gather(
            *[self.revise(
                instruction=f"""Enhance this analysis:
                - Add specific mathematical details and potential calculations
                - Identify any hidden constraints or boundary conditions
                - Cross-reference with other mathematical domains if applicable
                - Flag any ambiguous or underspecified elements in the problem""",
                context=analysis
            ) for analysis in raw_analyses]
        )

        # STEP 2: SYNTHESIZE PROBLEM CLASSIFICATION
        problem_classification = await self.ensemble(
            instruction="""Synthesize these three mathematical perspectives into a unified problem characterization:
            - Identify the PRIMARY mathematical domain (algebraic, geometric, combinatorial) and justify why
            - Note any SECONDARY domains that contribute to the solution
            - Specify the core solution strategy that integrates these perspectives
            - List all critical variables, constraints, and required intermediate results
            - Determine the expected answer format (single value, list, proof, etc.)
            Output as a structured JSON with keys: primary_domain, secondary_domains, core_strategy, variables, constraints, answer_format""",
            contexts_list=refined_analyses
        )

        # STEP 3: STRATEGIC DECOMPOSITION
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem based on the following classification:
            {problem_classification}
            
            Create subproblems with explicit dependencies:
            - Each subproblem must be solvable independently given its dependencies
            - Prioritize foundational subproblems (e.g., 'find equation of plane' before 'compute distance')
            - Mark computational subproblems suitable for Programmer operator
            - Mark conceptual subproblems requiring Generate/Revise operators
            - Include verification subproblems to validate critical steps
            Return list of subproblems with IDs, descriptions, and dependency lists.""",
            context=""
        )

        # STEP 4: PARALLEL SUBPROBLEM SOLVING WITH ADVERSARIAL VALIDATION
        async def solve_subproblem(subproblem):
            sub_id = subproblem['id']
            description = subproblem['description']
            dependencies = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
            
            # If dependencies exist, wait for them (in real implementation, you'd manage a dependency graph)
            # For this workflow, we'll assume topological order is handled externally or dependencies are minimal
            
            # Route to appropriate solver
            if any(keyword in description.lower() for keyword in ['compute', 'calculate', 'solve numerically', 'equation']):
                solution_attempt = await self.programmer(
                    instruction=f"""Solve this subproblem precisely:
                    {description}
                    
                    - Show all computational steps
                    - Use exact arithmetic (no floating point unless specified)
                    - Validate intermediate results for reasonableness
                    - Format final answer clearly""",
                    context=problem_classification
                )
            else:
                solution_attempt = await self.generate(
                    instruction=f"""Solve this conceptual subproblem:
                    {description}
                    
                    - Provide step-by-step reasoning
                    - Justify each step with mathematical principles
                    - Reference relevant theorems or identities
                    - Consider edge cases and special conditions""",
                    context=problem_classification
                )
            
            # Adversarial validation
            validation = await self.generate(
                instruction=f"""Critically evaluate this solution:
                {solution_attempt}
                
                - Check for logical consistency and mathematical correctness
                - Verify dimensional analysis (if applicable)
                - Test boundary conditions or special cases
                - Identify any assumptions that might not hold
                - Suggest improvements or corrections if needed
                Output 'VALID' if no issues, otherwise describe issues concisely.""",
                context=f"Subproblem: {description}"
            )
            
            # Revise if validation fails
            if "VALID" not in validation.upper():
                solution = await self.revise(
                    instruction=f"""Correct the solution based on this validation feedback:
                    {validation}
                    
                    - Address all identified issues
                    - Maintain mathematical rigor
                    - Preserve correct parts of original solution
                    - Output revised solution with clear corrections marked""",
                    context=solution_attempt
                )
            else:
                solution = solution_attempt
                
            return {"id": sub_id, "solution": solution, "validation": validation}

        # Solve all subproblems in parallel
        subproblem_results = await asyncio.gather(
            *[solve_subproblem(sp) for sp in decomposition]
        )

        # STEP 5: SYNTHESIZE FINAL SOLUTION
        # Convert results to context format
        solution_context = "\n\n".join([
            f"Subproblem {result['id']}:\n{result['solution']}\nValidation: {result['validation']}"
            for result in subproblem_results
        ])

        final_solution = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into a complete, coherent answer:
            - Integrate intermediate results logically
            - Ensure continuity of variables and units
            - Present final answer in the required format (from classification: {problem_classification})
            - Double-check that all problem constraints are satisfied
            - If answer is numerical, ensure it's an integer between 000-999 as required
            - If multiple answers, list them comma-separated
            - Box the final answer clearly""",
            context=solution_context
        )

        # STEP 6: SANITY CHECK ENSEMBLE
        sanity_checks = await asyncio.gather(
            self.generate(
                instruction="""Verify final answer using DIMENSIONAL ANALYSIS:
                - Check units consistency throughout solution
                - Verify orders of magnitude make physical/mathematical sense
                - Identify any dimensional mismatches""",
                context=final_solution
            ),
            self.generate(
                instruction="""Verify final answer using BOUNDARY CASE TESTING:
                - Test solution with extreme values or edge cases
                - Verify answer behaves as expected in limiting cases
                - Check for discontinuities or singularities""",
                context=final_solution
            ),
            self.generate(
                instruction="""Verify final answer using ALTERNATIVE METHOD:
                - Solve problem using a completely different mathematical approach
                - Compare result with original solution
                - Resolve any discrepancies""",
                context=final_solution
            )
        )

        # Final consensus
        final_answer = await self.ensemble(
            instruction="""Based on the original solution and three verification methods:
            - If all verifications agree, output the original answer
            - If discrepancies exist, identify the most reliable result and explain why
            - Ensure final answer is formatted as required (integer 000-999 or comma-separated list)
            - Output ONLY the final answer, nothing else""",
            contexts_list=[final_solution] + sanity_checks
        )

        return final_answer