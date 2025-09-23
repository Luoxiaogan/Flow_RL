# Workflow ID: limr_158_0
# Benchmark: limr
# Data Indices: [324, 23]

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

        # STEP 1: CLASSIFY PROBLEM & GENERATE STRATEGIES
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategy mapping:
            1. Identify primary mathematical domain(s): algebra, geometry, number theory, combinatorics, complex analysis, etc.
            2. List applicable advanced techniques: determinant analysis, generating functions, modular arithmetic, symmetry exploitation, etc.
            3. Propose 3 distinct solution strategies with brief rationale for each.
            4. Flag any constraints, boundary conditions, or implicit assumptions.
            5. Predict potential pitfalls or non-obvious insights required.
            Format as structured JSON with keys: "domains", "techniques", "strategies", "constraints", "pitfalls".""",
            context=""
        )

        # STEP 2: DECOMPOSE INTO SUBPROBLEMS
        decomposition = await self.decompose(
            instruction="""Decompose the problem into minimal, solvable subproblems:
            - Each subproblem should be independently addressable with clear inputs/outputs
            - Specify dependencies between subproblems
            - Prioritize subproblems that unlock subsequent steps
            - Include verification subproblems where possible
            Granularity: 3-7 subproblems total.""",
            context=classification
        )

        # STEP 3: PARALLEL STRATEGY EXECUTION (DIAMOND PATTERN)
        strategy_attempts = []
        strategy_list = json.loads(classification)["strategies"][:3]  # Top 3 strategies
        
        async def execute_strategy(strategy_desc, idx):
            return await self.generate(
                instruction=f"""Implement solution strategy {idx+1}:
                Strategy: {strategy_desc}
                
                Follow this protocol:
                1. Map strategy to subproblems from decomposition
                2. Solve subproblems in dependency order
                3. Show all intermediate steps with justifications
                4. Verify each sub-result where possible
                5. Combine into final answer candidate
                6. Self-critique: What could be wrong?""",
                context=f"Classification: {classification}\n\nDecomposition: {json.dumps(decomposition)}"
            )
        
        strategy_attempts = await asyncio.gather(
            *[execute_strategy(strategy["rationale"], i) for i, strategy in enumerate(strategy_list)]
        )

        # STEP 4: ENSEMBLE SYNTHESIS & SELECTION
        synthesized = await self.ensemble(
            instruction="""Synthesize and select the optimal solution:
            - Compare all strategy attempts for consistency, elegance, and correctness
            - Prefer solutions with explicit verification steps
            - Resolve contradictions by cross-validating with problem constraints
            - If multiple solutions agree, merge their strongest elements
            - Output final solution with clear step-by-step reasoning
            - Include confidence assessment (high/medium/low)""",
            contexts_list=strategy_attempts
        )

        # STEP 5: COMPUTATIONAL VERIFICATION
        verification_code = await self.generate(
            instruction="""Generate Python code to verify the final answer:
            - Implement mathematical relationships from original problem
            - Test with derived solution values
            - Include assertions for key constraints
            - Output should confirm correctness or flag discrepancies
            - Handle edge cases mentioned in constraints""",
            context=f"Final Solution: {synthesized}\n\nClassification: {classification}"
        )
        
        verification_result = await self.programmer(
            instruction="Execute verification code and report pass/fail with diagnostics",
            context=verification_code,
            max_retries=2
        )

        # STEP 6: REFINEMENT LOOP (MAX 2 ITERATIONS)
        current_solution = synthesized
        for iteration in range(2):
            if "PASS" in verification_result.upper() or "CORRECT" in verification_result.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise solution based on verification failure:
                Verification feedback: {verification_result}
                
                Required improvements:
                1. Correct computational errors
                2. Strengthen logical justifications
                3. Recheck constraint satisfaction
                4. Simplify if overcomplicated
                5. Ensure final answer format is integer 000-999
                
                Maintain mathematical rigor throughout.""",
                context=current_solution
            )
            
            # Re-verify
            verification_code = await self.generate(
                instruction="Generate updated verification code for revised solution",
                context=f"Revised Solution: {current_solution}\n\nOriginal Classification: {classification}"
            )
            verification_result = await self.programmer(
                instruction="Execute updated verification",
                context=verification_code,
                max_retries=2
            )

        # STEP 7: FINAL EXTRACTION & FORMATTING
        final_answer = await self.generate(
            instruction="""Extract final numerical answer with extreme precision:
            - Must be integer between 000 and 999
            - Verify against all problem constraints
            - If multiple candidates, select most verified
            - If no valid answer, output "ERROR"
            - Format as exactly three digits (e.g., "042", not "42")
            - Include one-sentence justification""",
            context=f"Final Solution: {current_solution}\n\nVerification: {verification_result}"
        )

        # STEP 8: SAFETY SUMMARIZATION
        return await self.summarize(
            instruction="""Condense to final answer only:
            - Extract exactly the three-digit integer
            - Remove all reasoning, justifications, and metadata
            - If extraction fails, return "000"
            - No punctuation, no units, no explanations""",
            context=final_answer
        )