# Workflow ID: limr_133_0
# Benchmark: limr
# Data Indices: [200, 275]

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

        # STEP 1: META-CLASSIFICATION - Understand problem nature
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this problem:
            1. Classify primary mathematical domain (combinatorics, algebra, geometry, number theory, optimization).
            2. Identify all variables, constraints, and hidden assumptions.
            3. Predict 2-3 most promising solution strategies (e.g., inclusion-exclusion, coordinate geometry, recursive relation).
            4. Flag any non-obvious transformations (e.g., 'this ratio problem can be solved via harmonic mean').
            5. Estimate difficulty level (1-5) and potential pitfalls.
            Format as structured JSON-like output with clear sections.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY EXPLORATION
        # Dynamically craft instructions based on analysis
        strategy_tasks = []

        # Strategy 1: Domain-specific approach (based on classification)
        domain_strategy = await self.generate(
            instruction=f"""Based on this analysis: {problem_analysis}
            Develop a complete solution using the PRIMARY recommended strategy.
            - Show all steps explicitly
            - Justify each mathematical operation
            - Verify against constraints
            - Output final answer as integer 000-999""",
            context=problem_analysis
        )
        strategy_tasks.append(domain_strategy)

        # Strategy 2: Alternative approach (different domain or method)
        alt_strategy = await self.generate(
            instruction=f"""Despite the primary classification in: {problem_analysis}
            Solve using an ALTERNATIVE mathematical domain or method.
            Example: if classified as algebra, try combinatorial reasoning.
            - Show complete working
            - Explain why this alternative is valid
            - Cross-validate with primary approach
            - Output final answer as integer 000-999""",
            context=problem_analysis
        )
        strategy_tasks.append(alt_strategy)

        # Strategy 3: Brute-force computational approach (safety net)
        code_strategy = await self.programmer(
            instruction=f"""Generate Python code to solve this problem computationally:
            - Model all constraints explicitly
            - Iterate through possible solutions if needed
            - Validate against problem conditions
            - Output ONLY the integer answer (000-999)
            Use the analysis for context: {problem_analysis}""",
            context=problem_analysis
        )
        strategy_tasks.append(code_strategy)

        # Gather all strategy outputs
        strategy_results = await asyncio.gather(*strategy_tasks)

        # STEP 3: VALIDATION & REFINEMENT
        validation_tasks = []
        for i, result in enumerate(strategy_results):
            validated = await self.revise(
                instruction=f"""CRITICALLY REVIEW this solution (Strategy {i+1}):
                - Check for logical consistency and mathematical errors
                - Verify all constraints from original problem are satisfied
                - Ensure answer is integer 000-999 format
                - If flawed, provide corrected version
                - If robust, condense to final answer only
                Original analysis for context: {problem_analysis}""",
                context=result
            )
            validation_tasks.append(validated)
        
        validated_results = await asyncio.gather(*validation_tasks)

        # STEP 4: ENSEMBLE SYNTHESIS WITH CONFLICT RESOLUTION
        final_answer = await self.ensemble(
            instruction="""Synthesize these solutions into one definitive answer:
            1. If all solutions agree, output the consensus answer.
            2. If they conflict, identify root cause of disagreement (e.g., misapplied principle, calculation error).
            3. Resolve conflicts by cross-validating against original problem constraints.
            4. Output ONLY the integer answer in 000-999 format.
            5. If still uncertain, prioritize computational (code) solution as tiebreaker.""",
            contexts_list=validated_results
        )

        # STEP 5: DECOMPOSITION FALLBACK (if answer is non-integer or unclear)
        # Check if final answer is a clean integer
        match = re.search(r'\b\d{1,3}\b', final_answer)
        if not match:
            # Trigger decomposition as last resort
            subproblems = await self.decompose(
                instruction="""Break this problem into minimal atomic subproblems:
                - Each subproblem must be independently solvable
                - Specify required mathematical tool for each (e.g., 'solve linear equation')
                - Order by dependency (prerequisites first)
                - Maximum 5 subproblems""",
                context=problem_analysis
            )
            
            # Solve subproblems sequentially
            subproblem_solutions = []
            for sp in subproblems:
                sp_solution = await self.generate(
                    instruction=f"""Solve this subproblem: {sp['description']}
                    Use ONLY the specified mathematical tool.
                    Show minimal working. Output ONLY the numerical result.""",
                    context=problem_analysis
                )
                subproblem_solutions.append(sp_solution)
            
            # Reassemble final answer
            reassembly = await self.generate(
                instruction=f"""Combine these subproblem solutions into final answer:
                Subproblems: {subproblem_solutions}
                Original problem: {self.problem_text}
                Output ONLY integer 000-999 format.""",
                context="\n".join(subproblem_solutions)
            )
            final_answer = reassembly

        # Final cleanup - ensure 3-digit format
        final_match = re.search(r'\b(\d{1,3})\b', final_answer)
        if final_match:
            answer_num = int(final_match.group(1))
            return f"{answer_num:03d}"
        else:
            # Ultimate fallback - return 000 if all else fails (shouldn't happen)
            return "000"