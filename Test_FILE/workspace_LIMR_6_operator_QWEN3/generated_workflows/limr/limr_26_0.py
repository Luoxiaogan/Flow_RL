# Workflow ID: limr_26_0
# Benchmark: limr
# Data Indices: [116, 72]

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

        # PHASE 1: PROBLEM CLASSIFICATION & ENTITY EXTRACTION
        classification = await self.generate(
            instruction="""Perform deep problem classification and entity extraction:
            1. Identify the primary mathematical domain (geometry, number theory, combinatorics, algebra, probability, etc.)
            2. List all given quantities, variables, and constraints with their symbolic representations
            3. Identify the target quantity to solve for
            4. Note any implicit assumptions or standard conventions that apply
            5. Determine if the problem requires exact computation, proof, optimization, or counting
            6. Assess whether multiple solution approaches are likely viable
            Format your response as a structured analysis with clear section headings.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            """Develop a solution strategy based on ALGEBRAIC and SYMBOLIC manipulation:
            - Express all relationships as equations or inequalities
            - Look for substitutions, symmetries, or transformations that simplify the problem
            - Consider polynomial, functional, or recursive formulations
            - Avoid numerical computation unless absolutely necessary""",
            
            """Develop a solution strategy based on GEOMETRIC and VISUAL reasoning:
            - Sketch a mental diagram of the problem setup
            - Identify similar triangles, congruent figures, or symmetry axes
            - Apply coordinate geometry if helpful
            - Use vector or trigonometric relationships where applicable""",
            
            """Develop a solution strategy based on COMBINATORIAL or PROBABILISTIC reasoning:
            - Identify sample spaces, events, or counting principles
            - Consider permutations, combinations, or generating functions
            - Look for recursive structures or state transitions
            - Apply expected value or conditional probability if relevant""",
            
            """Develop a solution strategy based on NUMBER THEORETIC or MODULAR reasoning:
            - Factorize given numbers or expressions
            - Apply divisibility rules, modular arithmetic, or Diophantine techniques
            - Consider prime factorizations or Euler's theorem
            - Look for patterns in sequences or residues"""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # PHASE 3: HIERARCHICAL DECOMPOSITION & PARALLEL EXECUTION
        async def execute_strategy(strategy_text):
            try:
                # Decompose the strategy into subproblems
                subproblems = await self.decompose(
                    instruction="""Break this solution strategy into discrete, ordered subproblems:
                    - Each subproblem should be self-contained and solvable with clear inputs/outputs
                    - Specify dependencies between subproblems
                    - Prioritize subproblems that can be computed or verified independently
                    - Include at least one verification step for critical calculations""",
                    context=strategy_text
                )
                
                # Execute subproblems in dependency order
                results = {}
                for sp in subproblems:
                    deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
                    # Wait for dependencies
                    dep_results = [results.get(dep_id.strip()) for dep_id in deps if dep_id.strip() in results]
                    dep_context = "\n".join([f"Dependency {i+1}: {res}" for i, res in enumerate(dep_results)]) if dep_results else ""
                    
                    # Choose execution method based on subproblem type
                    if any(kw in sp['description'].lower() for kw in ['compute', 'calculate', 'numerical', 'count', 'sum', 'product']):
                        step_result = await self.programmer(
                            instruction=f"""Execute this computational subproblem:
                            {sp['description']}
                            
                            Guidelines:
                            - Use exact arithmetic (fractions, integers) not floating point
                            - Verify intermediate results with assertions
                            - If recursion is needed, implement memoization
                            - Return only the final result, no explanations""",
                            context=dep_context
                        )
                    else:
                        step_result = await self.generate(
                            instruction=f"""Solve this conceptual subproblem:
                            {sp['description']}
                            
                            Guidelines:
                            - Show all logical steps
                            - Reference relevant theorems or identities
                            - Cross-verify with given constraints
                            - If stuck, propose an alternative approach""",
                            context=dep_context
                        )
                        # Revise for rigor
                        step_result = await self.revise(
                            instruction="""Improve this solution step:
                            - Verify all mathematical operations are valid
                            - Check for sign errors, domain restrictions, or division by zero
                            - Ensure all variables are properly defined
                            - Add missing justifications for non-obvious steps""",
                            context=step_result
                        )
                    
                    results[sp['id']] = step_result
                
                # Synthesize final answer from subproblem results
                synthesis = await self.generate(
                    instruction="""Synthesize a complete solution from these subproblem results:
                    - Combine results in logical order
                    - Verify consistency between subproblem outputs
                    - Isolate the final numerical answer
                    - Ensure answer is an integer between 000 and 999
                    - If multiple answers exist, select the one that satisfies all constraints""",
                    context="\n".join([f"Subproblem {k}: {v}" for k, v in results.items()])
                )
                
                return synthesis
            except Exception as e:
                return f"STRATEGY FAILED: {str(e)}"

        # Execute all strategies in parallel
        strategy_results = await asyncio.gather(
            *[execute_strategy(strategy) for strategy in strategies]
        )

        # PHASE 4: ENSEMBLE SYNTHESIS & VERIFICATION
        final_answer = await self.ensemble(
            instruction="""Select and synthesize the best solution from these candidates:
            - Evaluate each for mathematical rigor, completeness, and correctness
            - Prefer solutions that explicitly verify their results
            - Resolve discrepancies by cross-checking with original problem constraints
            - Extract the final numerical answer (must be integer 000-999)
            - If no candidate is fully correct, combine the most reliable parts
            - Output ONLY the three-digit integer answer, nothing else""",
            contexts_list=strategy_results
        )

        # PHASE 5: FINAL VALIDATION & FORMATTING
        validated_answer = await self.revise(
            instruction="""Validate and format the final answer:
            1. Confirm the answer is an integer between 000 and 999
            2. Verify it satisfies all original problem constraints
            3. Check for common errors: off-by-one, sign flips, unit mismatches
            4. If answer is not in correct format, derive the correct one
            5. Output ONLY the three-digit number, padded with leading zeros if necessary""",
            context=final_answer
        )

        # Extract just the number using regex to ensure clean output
        match = re.search(r'\b\d{1,3}\b', validated_answer)
        if match:
            answer = int(match.group())
            return f"{answer:03d}"
        else:
            # Fallback: return first three digits found or default
            digits = re.findall(r'\d', validated_answer)
            if len(digits) >= 3:
                return ''.join(digits[:3])
            else:
                return "000"  # Ultimate fallback