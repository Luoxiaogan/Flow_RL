# Workflow ID: limr_41_0
# Benchmark: limr
# Data Indices: [229, 289]

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

        # STEP 1: CLASSIFY PROBLEM & MAP STRATEGIES
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategy mapping:
            1. Identify the primary mathematical domain (geometry, number theory, combinatorics, algebra, optimization).
            2. List all relevant subdomains or techniques (e.g., modular arithmetic, vector geometry, generating functions).
            3. For each applicable technique, explain WHY it's suitable (cite specific problem features).
            4. Identify potential pitfalls or misleading intuitions.
            5. Propose 2-3 high-level solution strategies with estimated complexity.
            6. Flag any constraints on answer format (e.g., must be integer 000-999, fraction simplification rules).
            Be brutally honest about what might go wrong.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY EXPLORATION
        strategy_sketches = await asyncio.gather(
            self.generate(
                instruction=f"""Explore ALGEBRAIC/ANALYTIC approach:
                Based on classification: {classification}
                
                - Translate problem into equations/variables
                - Identify symmetries or invariants
                - Propose transformation (substitution, coordinate change, etc.)
                - Outline step-by-step without full computation
                - Estimate computational complexity and risk points""",
                context=""
            ),
            self.generate(
                instruction=f"""Explore GEOMETRIC/SPATIAL approach:
                Based on classification: {classification}
                
                - Identify geometric objects and relationships
                - Propose coordinate system or vector representation
                - Consider projections, symmetries, or invariants
                - Outline construction or calculation path
                - Flag any geometric impossibilities or edge cases""",
                context=""
            ),
            self.generate(
                instruction=f"""Explore COMBINATORIAL/NUMBER THEORETIC approach:
                Based on classification: {classification}
                
                - Identify counting principles or number patterns
                - Consider modular arithmetic, prime factors, or recursive structures
                - Propose generating functions, inclusion-exclusion, or bijections
                - Outline combinatorial argument or number-theoretic proof
                - Identify potential overcounting or divisibility traps""",
                context=""
            )
        )

        # STEP 3: SYNTHESIZE BEST APPROACH
        selected_strategy = await self.ensemble(
            instruction="""Select and synthesize the most promising solution approach:
            - Compare mathematical soundness and completeness
            - Evaluate risk of hidden assumptions or edge cases
            - Prefer approaches with built-in verification opportunities
            - Synthesize elements from multiple sketches if beneficial
            - Output must include: chosen strategy, justification, and step-by-step outline""",
            contexts_list=strategy_sketches
        )

        # STEP 4: DECOMPOSE INTO SUBPROBLEMS
        subproblems = await self.decompose(
            instruction="""Break down the selected strategy into atomic, verifiable subproblems:
            - Each subproblem should be solvable independently
            - Specify exact inputs and expected outputs
            - Identify dependencies between subproblems
            - Flag which subproblems are suitable for computational verification
            - Include sanity checks for each subproblem""",
            context=selected_strategy
        )

        # STEP 5: SOLVE SUBPROBLEMS WITH DUAL VERIFICATION
        subproblem_results = []
        for i, sp in enumerate(subproblems):
            # Solve via primary strategy
            primary_solution = await self.generate(
                instruction=f"""Solve subproblem using primary strategy:
                Subproblem: {sp['description']}
                Dependencies: {sp.get('dependencies', 'none')}
                Strategy context: {selected_strategy}
                
                - Show all steps with mathematical justification
                - Include intermediate results for verification
                - State assumptions explicitly""",
                context=""
            )
            
            # Verify via computational method if applicable
            try:
                computational_verification = await self.programmer(
                    instruction=f"""Verify subproblem computationally:
                    Subproblem: {sp['description']}
                    Expected output format: [specify numerical, boolean, etc.]
                    Constraints: {selected_strategy}
                    
                    - Write self-validating Python code with assertions
                    - Include boundary checks and sanity tests
                    - If verification fails, raise explicit error
                    - Return only the verified result""",
                    context=primary_solution,
                    max_retries=2
                )
                
                # Cross-validate results
                validation = await self.generate(
                    instruction=f"""Cross-validate primary and computational results:
                    Primary: {primary_solution}
                    Computational: {computational_verification}
                    
                    - Are results consistent?
                    - If not, identify source of discrepancy
                    - Propose resolution strategy
                    - Output final verified result for this subproblem""",
                    context=""
                )
                subproblem_results.append(validation)
                
            except Exception:
                # Fallback: use primary solution with warning
                subproblem_results.append(f"[UNVERIFIED] {primary_solution}")

        # STEP 6: SYNTHESIZE FINAL SOLUTION
        final_solution_draft = await self.generate(
            instruction=f"""Synthesize complete solution from verified subproblems:
            Subproblem results: {'; '.join(subproblem_results)}
            Original strategy: {selected_strategy}
            
            - Reconstruct full solution path
            - Ensure logical flow between subproblems
            - Highlight any remaining assumptions
            - State final answer in required format (integer 000-999)""",
            context=""
        )

        # STEP 7: FINAL VALIDATION & FORMATTING
        final_answer = await self.revise(
            instruction="""Final validation and formatting:
            - Verify answer is integer between 000 and 999
            - Check consistency with all problem constraints
            - Ensure no calculation errors in final steps
            - Format as 3-digit string with leading zeros if necessary
            - If multiple candidates, select most consistent with verification steps
            - Output ONLY the 3-digit answer, nothing else""",
            context=final_solution_draft
        )

        # Extract 3-digit answer
        match = re.search(r'\b(\d{3})\b', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: return first 3 digits found
            digits = re.findall(r'\d', final_answer)
            if len(digits) >= 3:
                return ''.join(digits[:3])
            else:
                return "000"  # Ultimate fallback