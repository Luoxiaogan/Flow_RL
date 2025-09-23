# Workflow ID: limr_141_0
# Benchmark: limr
# Data Indices: [234, 146]

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
        
        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGY SELECTION
        classification = await self.generate(
            instruction="""Perform deep structural analysis of this mathematical problem:
            1. Identify primary domain (geometry, algebra, number theory, combinatorics, etc.)
            2. List all mathematical objects involved (vectors, polynomials, complex numbers, etc.)
            3. Extract explicit constraints and implicit assumptions
            4. Predict likely solution approaches (coordinate geometry, modular arithmetic, generating functions, etc.)
            5. Estimate complexity level (number of steps, need for decomposition)
            6. Flag any potential traps or non-obvious insights required
            Output as structured JSON with keys: domain, objects, constraints, approaches, complexity, traps""",
            context=""
        )
        
        # PHASE 2: PARALLEL SOLUTION HYPOTHESIS GENERATION
        # Generate 3 different solution approaches based on classification
        approach_instructions = [
            """Develop a geometric/visual solution approach:
            - Create coordinate system if applicable
            - Identify key geometric relationships
            - Use properties of shapes, angles, and transformations
            - Show step-by-step geometric reasoning
            - Convert to numerical answer when possible""",
            
            """Develop an algebraic/symbolic solution approach:
            - Set up equations based on given constraints
            - Apply algebraic manipulations and identities
            - Look for symmetry or substitution opportunities
            - Reduce to solvable form
            - Show all algebraic steps clearly""",
            
            """Develop a computational/algorithmic solution approach:
            - Identify what needs to be computed
            - Break into computational steps
            - Specify any formulas or theorems to apply
            - Prepare for potential programming implementation
            - Show logical flow of calculations"""
        ]
        
        # Generate initial solution hypotheses in parallel
        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in approach_instructions]
        )
        
        # PHASE 3: SOLUTION REFINEMENT & VERIFICATION
        refined_hypotheses = []
        for i, hypothesis in enumerate(hypotheses):
            # First refinement: add rigor and check for errors
            refined = await self.revise(
                instruction=f"""Critically refine this solution hypothesis:
                1. Verify each mathematical step for logical consistency
                2. Check that all given constraints are satisfied
                3. Ensure no division by zero or invalid operations
                4. Add missing justifications for non-obvious steps
                5. Format clearly with step numbers
                6. Highlight the final numerical answer if reached
                Approach type: {['Geometric', 'Algebraic', 'Computational'][i]}""",
                context=hypothesis
            )
            refined_hypotheses.append(refined)
        
        # PHASE 4: COMPUTATIONAL VERIFICATION (where applicable)
        # Extract computational subproblems and solve them
        computational_checks = []
        for i, hypothesis in enumerate(refined_hypotheses):
            try:
                # Identify if this hypothesis contains computable elements
                computation_task = await self.generate(
                    instruction="""Extract any computational subproblems from this solution that could be verified by code:
                    - Equations to solve
                    - Sums or products to calculate
                    - Geometric measurements to compute
                    - Combinatorial counts to verify
                    If none, return "NO COMPUTATION NEEDED"
                    Otherwise, specify exactly what to compute and provide necessary inputs""",
                    context=hypothesis
                )
                
                if "NO COMPUTATION NEEDED" not in computation_task.upper():
                    computation_result = await self.programmer(
                        instruction=f"""Implement and execute code to solve this computational subproblem:
                        {computation_task}
                        Return only the numerical result and any relevant verification""",
                        context=hypothesis,
                        max_retries=3
                    )
                    computational_checks.append(f"Approach {i+1} Computation: {computation_result}")
                else:
                    computational_checks.append(f"Approach {i+1}: No computation needed")
            except Exception:
                computational_checks.append(f"Approach {i+1}: Computation failed")
        
        # PHASE 5: ENSEMBLE SYNTHESIS & FINAL ANSWER EXTRACTION
        synthesis_context = "\n\n".join([
            f"APPROACH {i+1} ({['Geometric', 'Algebraic', 'Computational'][i]}):\n{hyp}\n\nCOMPUTATION: {comp}"
            for i, (hyp, comp) in enumerate(zip(refined_hypotheses, computational_checks))
        ])
        
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution from all approaches:
            1. Compare all three solution approaches and their computational verifications
            2. Identify which approach is most rigorous and complete
            3. Resolve any conflicts between approaches
            4. Combine insights from multiple approaches if beneficial
            5. Extract the final numerical answer (must be integer 000-999)
            6. Format answer as: "FINAL ANSWER: XXX" where XXX is the 3-digit integer
            7. If uncertain, indicate confidence level and reasoning""",
            contexts_list=[synthesis_context]
        )
        
        # PHASE 6: FINAL VALIDATION & FORMATTING
        final_answer = await self.revise(
            instruction="""Final validation and formatting:
            1. Extract the final numerical answer from the synthesized solution
            2. Verify it's an integer between 000 and 999
            3. If not, re-examine the solution for errors
            4. Format as exactly 3 digits with leading zeros if needed
            5. Return ONLY the 3-digit number, nothing else""",
            context=synthesized_solution
        )
        
        # Clean extraction of the 3-digit answer
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            answer = match.group(1).zfill(3)
            if len(answer) == 3 and answer.isdigit():
                return answer
        
        # Fallback: extract any 3-digit number from the synthesis
        fallback_match = re.search(r'\b\d{3}\b', synthesized_solution)
        if fallback_match:
            return fallback_match.group(0)
        
        # Last resort: return 000 (should never happen with proper validation)
        return "000"