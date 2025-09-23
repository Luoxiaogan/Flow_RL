# Workflow ID: limr_127_0
# Benchmark: limr
# Data Indices: [279, 159]

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
        import json

        # PHASE 1: Problem Deconstruction and Strategy Generation
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, solvable subproblems. For each:
            - State what needs to be computed or proven
            - List required inputs or prior knowledge
            - Identify mathematical domain (algebra, combinatorics, etc.)
            - Note any constraints or boundary conditions
            Output as structured list with clear dependencies.""",
            context=""
        )

        decomposition_summary = await self.summarize(
            instruction="""Condense the decomposition into a roadmap:
            - List key subproblems in logical order
            - Highlight critical dependencies
            - Flag any subproblems that seem ambiguous or underspecified
            - Suggest default strategies for each (e.g., 'use inclusion-exclusion', 'apply quadratic formula')""",
            context=str(decomposition)
        )

        # Generate 3 parallel solution strategies
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop a ALGEBRAIC/SYMBOLIC solution strategy:
                - Use formal mathematical notation
                - Prioritize exact derivations over approximations
                - Leverage theorems and identities from relevant domains
                - Structure as: 1) Restate problem formally, 2) Apply key insight, 3) Derive step-by-step, 4) Verify constraints
                Problem context: {decomposition_summary}""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a COMBINATORIAL/PROBABILISTIC solution strategy:
                - Focus on counting, symmetry, or probabilistic reasoning
                - Enumerate cases if feasible
                - Use combinatorial identities or generating functions
                - Structure as: 1) Define sample space, 2) Identify favorable outcomes, 3) Compute ratio/probability, 4) Scale to integer answer
                Problem context: {decomposition_summary}""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a COMPUTATIONAL/SIMULATION strategy:
                - Design a brute-force or algorithmic approach
                - Specify data structures and termination conditions
                - Handle edge cases explicitly
                - Structure as: 1) Define search space, 2) Implement validation checks, 3) Execute computation, 4) Extract integer result
                Problem context: {decomposition_summary}""",
                context=""
            )
        ]
        strategy_results = await asyncio.gather(*strategy_tasks)

        # PHASE 2: Parallel Strategy Execution with Validation
        async def execute_strategy(strategy, strategy_name):
            try:
                # Refine strategy with decomposition context
                refined_strategy = await self.revise(
                    instruction=f"""Improve this {strategy_name} strategy:
                    - Fill any logical gaps
                    - Add missing mathematical justifications
                    - Ensure all steps are computable or provable
                    - Format for direct implementation""",
                    context=strategy
                )
                
                # Attempt computational solution if applicable
                code_result = ""
                if "COMPUTATIONAL" in strategy_name or "ALGEBRAIC" in strategy_name:
                    code_result = await self.programmer(
                        instruction=f"""Implement the {strategy_name} strategy as Python code:
                        - Use exact arithmetic (fractions, integers)
                        - Validate intermediate results
                        - Return ONLY the final integer answer (000-999)
                        - If multiple answers possible, return most probable
                        Strategy: {refined_strategy}""",
                        context=refined_strategy,
                        max_retries=2
                    )
                
                # Summarize execution path
                execution_summary = await self.summarize(
                    instruction=f"""Summarize the {strategy_name} solution path:
                    - State final answer (if any)
                    - Note any errors or uncertainties
                    - Rate confidence (high/medium/low) based on: 
                      a) Completeness of steps, 
                      b) Computational success, 
                      c) Consistency with problem constraints
                    - Justify confidence rating""",
                    context=f"Strategy: {refined_strategy}\nCode Result: {code_result}"
                )
                
                return {
                    "strategy": strategy_name,
                    "answer": self._extract_integer_answer(execution_summary),
                    "confidence": self._extract_confidence(execution_summary),
                    "summary": execution_summary
                }
            except Exception as e:
                return {
                    "strategy": strategy_name,
                    "answer": None,
                    "confidence": "low",
                    "summary": f"Execution failed: {str(e)}"
                }

        # Execute all strategies in parallel
        execution_tasks = [
            execute_strategy(strategy_results[0], "ALGEBRAIC"),
            execute_strategy(strategy_results[1], "COMBINATORIAL"),
            execute_strategy(strategy_results[2], "COMPUTATIONAL")
        ]
        execution_results = await asyncio.gather(*execution_tasks)

        # PHASE 3: Confidence-Weighted Ensemble Synthesis
        valid_results = [r for r in execution_results if r["answer"] is not None]
        
        if len(valid_results) == 0:
            # Fallback: Lateral thinking
            lateral_strategy = await self.generate(
                instruction="""Reframe the problem using an analogy from a different mathematical domain:
                - If algebraic, try geometric interpretation
                - If combinatorial, try number-theoretic approach
                - If computational, try analytical solution
                Propose a new solution pathway and compute answer.""",
                context=str(decomposition_summary)
            )
            lateral_answer = await self.programmer(
                instruction="""Implement the lateral thinking strategy:
                - Focus on extracting integer answer 000-999
                - Use any mathematical domain necessary
                - Return only the final integer""",
                context=lateral_strategy
            )
            final_answer = self._extract_integer_answer(lateral_answer)
        else:
            # Synthesize with confidence weighting
            synthesis = await self.ensemble(
                instruction="""Synthesize these solution attempts:
                - Compare answers and confidence ratings
                - If consensus (≥2 agree), select majority answer
                - If conflict, identify most mathematically rigorous justification
                - Reconcile discrepancies by finding root cause of errors
                - Output ONLY the final integer answer (000-999)""",
                contexts_list=[r["summary"] for r in valid_results]
            )
            final_answer = self._extract_integer_answer(synthesis)

        # FINAL VALIDATION: One-sentence proof
        validation = await self.generate(
            instruction=f"""Given answer {final_answer}, construct:
            1) One-sentence proof that this answer is correct
            2) One-sentence explanation why common alternatives ({final_answer-1}, {final_answer+1}) are wrong
            If unable to construct coherent proof, return 'RETRY'""",
            context=str(execution_results)
        )
        
        if "RETRY" in validation:
            # Simple fallback: return highest confidence answer
            sorted_results = sorted(valid_results, key=lambda x: x["confidence"], reverse=True)
            final_answer = sorted_results[0]["answer"] if sorted_results else "000"

        return str(final_answer).zfill(3)

    def _extract_integer_answer(self, text):
        """Extract integer answer from text, ensuring it's in 000-999 range"""
        import re
        matches = re.findall(r'\b([0-9]{1,3})\b', text)
        for match in matches:
            num = int(match)
            if 0 <= num <= 999:
                return num
        return None

    def _extract_confidence(self, text):
        """Extract confidence rating from text"""
        text = text.lower()
        if "high" in text:
            return "high"
        elif "medium" in text:
            return "medium"
        else:
            return "low"