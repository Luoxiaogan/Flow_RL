# Workflow ID: limr_24_0
# Benchmark: limr
# Data Indices: [155, 314]

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

        # PHASE 1: PARALLEL INTERPRETATION LENSES
        # Generate multiple mathematical perspectives simultaneously
        algebraic_lens = await self.generate(
            instruction="""Interpret this problem through an algebraic lens:
            - Identify all variables, equations, and functional relationships
            - Look for polynomial, recursive, or functional equation structures
            - Consider substitutions or transformations that simplify complexity
            - Note any symmetries or invariants in algebraic form
            - Suggest potential algebraic solution pathways""",
            context=""
        )

        combinatorial_lens = await self.generate(
            instruction="""Interpret this problem through a combinatorial/probabilistic lens:
            - Identify counting principles, permutations, combinations, or probability distributions
            - Look for linearity of expectation, symmetry in counting, or combinatorial identities
            - Consider sample spaces, events, and expected values
            - Note any overcounting/undercounting risks or combinatorial bounds
            - Suggest potential combinatorial solution pathways""",
            context=""
        )

        geometric_lens = await self.generate(
            instruction="""Interpret this problem through a geometric/spatial lens:
            - Identify geometric objects, dimensions, coordinates, or spatial relationships
            - Look for symmetries, similar triangles, coordinate transformations, or vector operations
            - Consider trigonometric identities, distance formulas, or area/volume relationships
            - Note any geometric invariants or extremal principles
            - Suggest potential geometric solution pathways""",
            context=""
        )

        number_theoretic_lens = await self.generate(
            instruction="""Interpret this problem through a number-theoretic lens:
            - Identify modular arithmetic, divisibility, prime factors, or Diophantine structures
            - Look for patterns in residues, gcd/lcm relationships, or multiplicative functions
            - Consider Chinese Remainder Theorem, Fermat's Little Theorem, or Euler's Theorem applications
            - Note any periodicities or congruence classes
            - Suggest potential number-theoretic solution pathways""",
            context=""
        )

        # PHASE 2: SYNTHESIZE INTERPRETATIONS AND DECOMPOSE
        lens_synthesis = await self.ensemble(
            instruction="""Synthesize these mathematical interpretations into a unified problem understanding:
            - Identify overlapping insights across lenses (these are likely structural invariants)
            - Resolve any contradictions between interpretations
            - Prioritize solution pathways that appear in multiple lenses
            - Construct a meta-description of the problem's core mathematical essence
            - Flag any lens that seems irrelevant or misleading for this problem""",
            contexts_list=[algebraic_lens, combinatorial_lens, geometric_lens, number_theoretic_lens]
        )

        # Decompose based on synthesized understanding
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem using the synthesized understanding:
            {lens_synthesis}
            
            Break into atomic subproblems with clear dependencies:
            - Each subproblem should be solvable independently given its dependencies
            - Identify "keystone" subproblems whose solution unlocks multiple downstream steps
            - Prioritize subproblems that appear across multiple mathematical lenses
            - Include verification subproblems that can validate intermediate results
            - Structure dependencies to allow parallel solving where possible""",
            context=lens_synthesis
        )

        # PHASE 3: PARALLEL SUBPROBLEM SOLVING WITH CONDITIONAL ROUTING
        subproblem_solutions = {}
        keystone_solutions = {}

        # Solve subproblems in parallel, routing based on type
        async def solve_subproblem(subproblem):
            sub_id = subproblem['id']
            description = subproblem['description']
            
            # Route to appropriate solver based on content
            if any(keyword in description.lower() for keyword in ['compute', 'calculate', 'sum', 'product', 'value']):
                # Route to programmer for computational subproblems
                solution = await self.programmer(
                    instruction=f"""Solve this computational subproblem exactly:
                    {description}
                    
                    Requirements:
                    - Use symbolic computation where possible
                    - Avoid floating point approximations
                    - Return exact fractions, radicals, or integers as needed
                    - Show intermediate steps in comments
                    - Validate result against problem constraints""",
                    context=lens_synthesis
                )
            elif any(keyword in description.lower() for keyword in ['prove', 'show', 'demonstrate', 'verify']):
                # Route to generate/revise for proof-based subproblems
                initial_proof = await self.generate(
                    instruction=f"""Construct a rigorous proof for:
                    {description}
                    
                    Requirements:
                    - Use formal mathematical reasoning
                    - Reference relevant theorems or principles
                    - Include all logical steps
                    - Consider edge cases and counterexamples""",
                    context=lens_synthesis
                )
                solution = await self.revise(
                    instruction="""Strengthen this proof:
                    - Fill any logical gaps
                    - Add missing justifications
                    - Ensure all assumptions are explicit
                    - Verify against potential counterexamples
                    - Format as a clean, rigorous mathematical argument""",
                    context=initial_proof
                )
            else:
                # Default to generate for conceptual/structural subproblems
                solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {description}
                    
                    Requirements:
                    - Provide clear, step-by-step reasoning
                    - Connect to the broader problem context
                    - Justify each step mathematically
                    - Consider alternative approaches and why this one is optimal""",
                    context=lens_synthesis
                )
            
            return sub_id, solution

        # Solve all subproblems concurrently
        subproblem_tasks = [solve_subproblem(sp) for sp in decomposition]
        subproblem_results = await asyncio.gather(*subproblem_tasks)
        subproblem_solutions = {sub_id: solution for sub_id, solution in subproblem_results}

        # Identify and solve keystone subproblems first (if any marked as such)
        keystone_ids = []
        for sp in decomposition:
            if 'keystone' in sp['description'].lower() or 'critical' in sp['description'].lower():
                keystone_ids.append(sp['id'])

        if keystone_ids:
            keystone_context = "\n\n".join([f"Subproblem {sub_id}: {subproblem_solutions[sub_id]}" for sub_id in keystone_ids])
            
            # Revise decomposition based on keystone solutions
            revised_decomposition = await self.decompose(
                instruction=f"""Revise the problem decomposition based on these keystone solutions:
                {keystone_context}
                
                Update:
                - Modify dependent subproblems to incorporate keystone results
                - Eliminate any subproblems made redundant by keystone solutions
                - Add new subproblems that become apparent given keystone insights
                - Re-prioritize remaining subproblems based on new dependencies""",
                context=keystone_context
            )
            
            # Solve any new or revised subproblems
            additional_tasks = []
            for sp in revised_decomposition:
                if sp['id'] not in subproblem_solutions:
                    additional_tasks.append(solve_subproblem(sp))
            
            if additional_tasks:
                additional_results = await asyncio.gather(*additional_tasks)
                for sub_id, solution in additional_results:
                    subproblem_solutions[sub_id] = solution

        # PHASE 4: CONSISTENCY VERIFICATION AND SYNTHESIS
        # Create consistency check across all subproblem solutions
        all_solutions_text = "\n\n".join([f"Subproblem {sub_id}: {solution}" for sub_id, solution in subproblem_solutions.items()])
        
        consistency_check = await self.generate(
            instruction=f"""Perform a consistency verification across all subproblem solutions:
            {all_solutions_text}
            
            Check for:
            - Mathematical contradictions between subproblem results
            - Violations of problem constraints or initial conditions
            - Dimensional or unit inconsistencies
            - Logical gaps in the overall solution chain
            - Potential off-by-one errors or boundary condition violations
            
            If inconsistencies found, identify which subproblem(s) need revision and why.""",
            context=all_solutions_text
        )

        # If inconsistencies found, revise problematic subproblems
        if "inconsistency" in consistency_check.lower() or "contradiction" in consistency_check.lower():
            # Extract subproblem IDs needing revision (simple pattern matching)
            import re
            problematic_ids = re.findall(r'Subproblem\s+([A-Za-z0-9]+)', consistency_check)
            
            for sub_id in problematic_ids:
                if sub_id in subproblem_solutions:
                    revised_solution = await self.revise(
                        instruction=f"""Revise this subproblem solution based on consistency issues:
                        {consistency_check}
                        
                        Requirements:
                        - Address the specific inconsistency mentioned
                        - Verify against all related subproblem solutions
                        - Ensure mathematical rigor and precision
                        - Maintain alignment with overall problem constraints""",
                        context=subproblem_solutions[sub_id]
                    )
                    subproblem_solutions[sub_id] = revised_solution

        # PHASE 5: FINAL SYNTHESIS AND ANSWER EXTRACTION
        final_synthesis = await self.ensemble(
            instruction="""Synthesize all subproblem solutions into a complete, coherent answer:
            - Construct a unified solution narrative that connects all subproblems
            - Resolve any remaining minor inconsistencies through mathematical reasoning
            - Extract the final numerical answer (integer between 000-999)
            - If answer is fractional p/q, compute p+q as final answer
            - Verify final answer satisfies all problem constraints and edge cases
            - Present final answer in format: "FINAL_ANSWER: XXX" where XXX is the integer""",
            contexts_list=list(subproblem_solutions.values())
        )

        # Extract final answer using regex
        answer_match = re.search(r'FINAL_ANSWER:\s*(\d{1,3})', final_synthesis)
        if answer_match:
            final_answer = answer_match.group(1).zfill(3)  # Ensure 3-digit format
        else:
            # Fallback: extract any 1-3 digit number from end of synthesis
            number_match = re.search(r'(\d{1,3})$', final_synthesis.strip())
            if number_match:
                final_answer = number_match.group(1).zfill(3)
            else:
                # Last resort: ask programmer to extract from synthesis
                final_answer_extraction = await self.programmer(
                    instruction="""Extract the final numerical answer from this synthesis:
                    The answer should be an integer between 000 and 999.
                    If the synthesis mentions a fraction p/q, compute p+q.
                    Return only the 3-digit answer with leading zeros if needed.""",
                    context=final_synthesis
                )
                # Clean the extraction
                clean_match = re.search(r'\d{1,3}', final_answer_extraction)
                final_answer = clean_match.group(0).zfill(3) if clean_match else "000"

        return final_answer