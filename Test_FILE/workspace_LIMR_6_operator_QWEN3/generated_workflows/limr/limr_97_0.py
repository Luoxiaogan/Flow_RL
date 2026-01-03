# Workflow ID: limr_97_0
# Benchmark: limr
# Data Indices: [85, 102]

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
        
        # PHASE 1: DECOMPOSE & CLASSIFY
        decomposition = await self.decompose(
            instruction="""Break this problem into atomic subproblems. For each:
            1. Describe what needs to be solved
            2. Classify as: computational, symbolic, structural, or hybrid
            3. Identify key mathematical domains involved (e.g., trig, combinatorics, geometry)
            4. List explicit and implicit constraints
            5. Note any required answer format (e.g., integer 000-999)
            Return as structured list with clear IDs and dependencies.""",
            context=""
        )
        
        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_tasks = []
        for subproblem in decomposition:
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            sp_class = "computational"  # Default, will be overridden by analysis
            
            # Dynamically generate strategy based on subproblem description
            classification = await self.generate(
                instruction=f"""Classify this subproblem precisely:
                Description: {sp_desc}
                
                Determine:
                - Primary type: computational (requires calculation), symbolic (requires algebra/trig manipulation), structural (requires combinatorial/geometric insight), or hybrid
                - Key mathematical tools needed
                - Potential solution approaches (list 2-3)
                - Known pitfalls or edge cases
                - Expected intermediate outputs
                
                Output as structured JSON-like text with clear labels.""",
                context=""
            )
            
            # Extract classification type for routing
            if "symbolic" in classification.lower():
                sp_class = "symbolic"
            elif "structural" in classification.lower():
                sp_class = "structural"
            elif "computational" in classification.lower():
                sp_class = "computational"
            
            # Generate 3 parallel solution strategies per subproblem
            strategies = [
                await self.generate(
                    instruction=f"""Strategy 1 for {sp_id}: BRUTE COMPUTATION
                    Subproblem: {sp_desc}
                    Classification: {classification}
                    
                    Generate Python code concept to solve this computationally.
                    - Identify variables and constraints
                    - Outline algorithmic approach
                    - Note precision requirements
                    - Consider edge cases and validation
                    Output as pseudo-code with comments.""",
                    context=""
                ),
                await self.generate(
                    instruction=f"""Strategy 2 for {sp_id}: SYMBOLIC MANIPULATION
                    Subproblem: {sp_desc}
                    Classification: {classification}
                    
                    Solve using algebraic/trigonometric identities and symbolic reasoning.
                    - List relevant identities or theorems
                    - Show step-by-step derivation
                    - Justify each transformation
                    - Handle special cases explicitly
                    Output as formal mathematical derivation.""",
                    context=""
                ),
                await self.generate(
                    instruction=f"""Strategy 3 for {sp_id}: STRUCTURAL INSIGHT
                    Subproblem: {sp_desc}
                    Classification: {classification}
                    
                    Solve using combinatorial, geometric, or pattern-based reasoning.
                    - Identify symmetries or invariants
                    - Propose clever transformations or substitutions
                    - Use counting principles or geometric properties
                    - Explain why this approach is efficient
                    Output as conceptual explanation with key insights.""",
                    context=""
                )
            ]
            
            # Refine each strategy
            refined_strategies = await asyncio.gather(
                *[self.revise(
                    instruction=f"""Improve this solution strategy for {sp_id}:
                    - Fill in missing steps
                    - Correct logical gaps
                    - Add validation checks
                    - Ensure alignment with problem constraints
                    - Format for clarity and precision""",
                    context=strat
                ) for strat in strategies]
            )
            
            # Ensemble best strategy per subproblem
            best_strategy = await self.ensemble(
                instruction=f"""Select the most promising strategy for {sp_id}:
                Criteria:
                1. Mathematical soundness
                2. Computational feasibility
                3. Alignment with problem constraints
                4. Elegance and insight
                5. Resistance to edge cases
                
                Justify your selection. Output selected strategy with enhancements.""",
                contexts_list=refined_strategies
            )
            
            strategy_tasks.append(best_strategy)
        
        # PHASE 3: SYNTHESIZE & COMPUTE
        all_strategies = "\n\n".join([f"Subproblem Strategy: {s}" for s in strategy_tasks])
        
        integrated_solution = await self.generate(
            instruction=f"""Integrate all subproblem strategies into unified solution:
            Strategies: {all_strategies}
            Decomposition: {decomposition}
            
            Steps:
            1. Order subproblems by dependency
            2. Resolve any conflicts between strategies
            3. Create end-to-end solution flow
            4. Identify final computation needed for integer answer 000-999
            5. Note any remaining uncertainties
            
            Output as complete, step-by-step solution draft.""",
            context=all_strategies
        )
        
        # PHASE 4: PROGRAMMATIC VALIDATION & COMPUTATION
        final_computation = await self.programmer(
            instruction=f"""Generate Python code to compute final answer:
            Solution draft: {integrated_solution}
            
            Requirements:
            - Compute exact integer answer between 000-999
            - Include validation assertions
            - Handle edge cases identified in decomposition
            - Use exact arithmetic (no floating point unless unavoidable)
            - Output only the final integer, formatted as 3-digit string (e.g., '042')
            
            If symbolic manipulation is needed, use sympy. If combinatorics, use math.comb or itertools as appropriate.""",
            context=integrated_solution,
            max_retries=3
        )
        
        # PHASE 5: VERIFY & FORMAT
        verification = await self.generate(
            instruction=f"""Verify final answer:
            Computed answer: {final_computation}
            Original problem: {self.problem_text}
            Solution draft: {integrated_solution}
            
            Check:
            1. Does answer satisfy all problem constraints?
            2. Is it in correct format (integer 000-999)?
            3. Are there alternative solutions that should be considered?
            4. Does it match dimensional/structural expectations?
            
            If any issues, propose correction. Otherwise, output 'VERIFIED: [answer]'.""",
            context=final_computation
        )
        
        # Extract final answer
        match = re.search(r'\b\d{1,3}\b', verification)
        if match:
            answer = int(match.group())
            return f"{answer:03d}"
        else:
            # Fallback: extract from programmer output
            match = re.search(r'\b\d{1,3}\b', final_computation)
            if match:
                answer = int(match.group())
                return f"{answer:03d}"
            else:
                # Last resort: return 000 (should rarely happen)
                return "000"