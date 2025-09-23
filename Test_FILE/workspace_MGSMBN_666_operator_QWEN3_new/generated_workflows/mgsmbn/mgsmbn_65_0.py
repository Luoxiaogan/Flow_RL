# Workflow ID: mgsmbn_65_0
# Benchmark: mgsmbn
# Data Indices: [45, 117]

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

        # STEP 1: Decompose the problem into subproblems with dependencies
        decomposition = await self.decompose(
            instruction="""Break this Bengali math word problem into minimal, solvable subproblems.
            For each subproblem:
            - State what needs to be calculated or determined
            - List dependencies (other subproblem IDs it relies on)
            - Identify units involved
            - Flag any ambiguities in wording or implicit constraints
            - If only one simple calculation is needed, mark as 'trivial'
            Output as structured list of dicts with keys: id, description, dependencies, units, flags.""",
            context=""
        )

        # STEP 2: Assess complexity to decide strategy
        complexity_analysis = await self.generate(
            instruction=f"""Analyze this decomposition:
            {json.dumps(decomposition, ensure_ascii=False, indent=2)}
            
            Determine:
            1. Is this a trivial problem (single step, no dependencies)? 
            2. Are there ambiguous or underspecified subproblems?
            3. What is your confidence (0-100%) that decomposition is complete?
            4. Suggest optimal solving strategy: direct, parallel, or hypothesis-based.
            
            Format: JSON with keys: trivial, ambiguous, confidence, strategy""",
            context=""
        )

        try:
            complexity = json.loads(complexity_analysis)
        except:
            # Fallback: treat as complex
            complexity = {"trivial": False, "ambiguous": True, "confidence": 50, "strategy": "hypothesis"}

        # STRATEGY A: Trivial problem — direct solve
        if complexity.get("trivial", False) and complexity.get("confidence", 0) > 80:
            direct_solution = await self.programmer(
                instruction="""Solve this single-step math problem.
                Extract the calculation needed, perform it with full precision,
                track units throughout, and return only the final numerical answer.
                If units are ambiguous, state assumption before calculating.""",
                context=""
            )
            # Extract number from programmer output
            import re
            match = re.search(r'[\d,]+\.?\d*', direct_solution)
            return float(match.group().replace(',', '')) if match else direct_solution

        # STRATEGY B: Complex problem — hierarchical parallel solve with validation
        elif complexity.get("strategy") in ["direct", "parallel"] or complexity.get("confidence", 0) > 60:
            
            # Topological sort of subproblems by dependency
            subproblem_map = {sp['id']: sp for sp in decomposition}
            solved = {}
            remaining = decomposition.copy()

            while remaining:
                # Find subproblems with all dependencies resolved
                ready = [
                    sp for sp in remaining 
                    if all(dep.strip() in solved for dep in sp.get('dependencies', '').split(',') if dep.strip())
                ]
                
                if not ready:
                    break  # Circular dependency or missing info

                # Solve ready subproblems in parallel
                async def solve_subproblem(sp):
                    sp_id = sp['id']
                    context_data = "\n".join([f"{k}: {v}" for k, v in solved.items()]) if solved else "No prior results"
                    
                    # First attempt
                    attempt = await self.generate(
                        instruction=f"""Solve subproblem: {sp['description']}
                        Units: {sp.get('units', 'unknown')}
                        Prior results: {context_data}
                        
                        Show step-by-step reasoning. Track units. Apply real-world constraints 
                        (no negative people, fractional items only if context allows).
                        Return final value with unit. If uncertain, state assumption.""",
                        context=""
                    )
                    
                    # Validate with critic
                    for retry in range(2):
                        critique = await self.generate(
                            instruction=f"""Critique this solution:
                            {attempt}
                            
                            Check for:
                            - Unit consistency
                            - Arithmetic errors
                            - Violation of real-world constraints
                            - Logical consistency with problem context
                            If no issues, respond 'VALID'. Otherwise, list specific errors.""",
                            context=attempt
                        )
                        
                        if "VALID" in critique.upper():
                            break
                        else:
                            attempt = await self.revise(
                                instruction=f"""Fix these issues:
                                {critique}
                                Maintain unit tracking and real-world plausibility.""",
                                context=attempt
                            )
                    
                    # Extract numerical value for chaining
                    import re
                    match = re.search(r'([\d,]+\.?\d*)\s*([^\d\s]*)$', attempt)
                    if match:
                        value = float(match.group(1).replace(',', ''))
                        unit = match.group(2).strip()
                        solved[sp_id] = f"{value} {unit}" if unit else str(value)
                    else:
                        solved[sp_id] = attempt  # Keep full text if extraction fails
                    
                    return sp_id

                # Execute ready subproblems in parallel
                await asyncio.gather(*[solve_subproblem(sp) for sp in ready])
                
                # Remove solved from remaining
                remaining = [sp for sp in remaining if sp['id'] not in solved]

            # Synthesize final answer
            synthesis = await self.ensemble(
                instruction=f"""Synthesize final answer from these subproblem results:
                {json.dumps(solved, ensure_ascii=False, indent=2)}
                
                Trace the logical flow from initial values to final answer.
                Verify unit consistency throughout the chain.
                If final answer should be unitless (e.g., count of people), remove unit.
                Return ONLY the final numerical value, nothing else.""",
                contexts_list=[json.dumps(solved, ensure_ascii=False)]
            )
            
            # Extract and return final number
            import re
            match = re.search(r'[\d,]+\.?\d*', synthesis)
            return float(match.group().replace(',', '')) if match else synthesis

        # STRATEGY C: Low confidence — parallel hypothesis generation
        else:
            hypotheses = await asyncio.gather(
                self.generate(
                    instruction="""Solve using ALGEBRAIC approach:
                    Define variables, write equations, solve symbolically.
                    Track units. Show all steps. Return final numerical value.""",
                    context=""
                ),
                self.generate(
                    instruction="""Solve using TABULAR approach:
                    Create a table of entities and their quantities.
                    Track changes step by step. Calculate final result.
                    Return final numerical value with unit reasoning.""",
                    context=""
                ),
                self.generate(
                    instruction="""Solve using VERBAL REASONING:
                    Explain in Bengali-like logical steps without formal math.
                    Use proportional reasoning, comparisons, or real-world analogies.
                    Derive final numerical answer.""",
                    context=""
                )
            )
            
            # Extract numerical answers from each
            def extract_number(text):
                import re
                match = re.search(r'[\d,]+\.?\d*', text)
                return float(match.group().replace(',', '')) if match else None
            
            numerical_hypotheses = [str(extract_number(h)) for h in hypotheses if extract_number(h) is not None]
            
            if len(numerical_hypotheses) == 0:
                # Fallback to programmer on original problem
                fallback = await self.programmer(
                    instruction="Solve this math word problem. Extract calculation and compute.",
                    context=""
                )
                match = re.search(r'[\d,]+\.?\d*', fallback)
                return float(match.group().replace(',', '')) if match else fallback
            
            # Ensemble vote
            final_answer = await self.ensemble(
                instruction="""Select the most consistent and well-reasoned answer.
                All hypotheses should converge on same value. If not, choose the one with:
                - Clearest unit tracking
                - Most explicit step-by-step reasoning
                - Best alignment with problem constraints
                Return ONLY the numerical value.""",
                contexts_list=numerical_hypotheses
            )
            
            return extract_number(final_answer) or final_answer