# Workflow ID: limr_7_0
# Benchmark: limr
# Data Indices: [19, 292]

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

        # Step 1: Classify the problem to guide strategy
        classification = await self.generate(
            instruction="""Thoroughly classify this mathematical problem by:
            1. Primary domain (geometry, number theory, combinatorics, algebra, etc.)
            2. Required techniques (proof, computation, optimization, counting, etc.)
            3. Expected answer format (integer 000-999, proof, etc.)
            4. Complexity level (low, medium, high) based on steps and insight required
            5. Potential solution approaches (list 2-3 distinct strategies)
            Provide structured, detailed classification to inform subsequent decomposition and parallel exploration.""",
            context=""
        )

        # Step 2: Decompose into subproblems
        subproblems = await self.decompose(
            instruction=f"""Based on classification:
            {classification}
            
            Decompose the problem into minimal, solvable subproblems. For each:
            - Clearly state what needs to be found or proven
            - Specify dependencies on other subproblems
            - Indicate which mathematical tools are likely required
            Ensure decomposition is hierarchical and logically ordered.""",
            context=classification
        )

        # Step 3: Generate parallel solution attempts for each subproblem
        async def solve_subproblem(subproblem):
            # Generate initial solution attempt
            attempt = await self.generate(
                instruction=f"""Solve this subproblem using appropriate mathematical reasoning:
                Subproblem: {subproblem['description']}
                Dependencies: {subproblem.get('dependencies', 'None')}
                
                Show all steps, justify key insights, and maintain mathematical rigor.
                If computational, describe algorithm before executing.""",
                context=classification
            )
            
            # Verify and revise up to twice
            for _ in range(2):
                verification = await self.revise(
                    instruction="""Critically verify this solution:
                    - Check logical consistency and mathematical correctness
                    - Verify all constraints and conditions are satisfied
                    - Identify any gaps, errors, or unjustified assumptions
                    If errors found, correct them and explain the correction.""",
                    context=attempt
                )
                if "error" not in verification.lower() and "incorrect" not in verification.lower() and "fix" not in verification.lower():
                    break
                attempt = verification
            
            # Summarize the verified solution
            return await self.summarize(
                instruction="Extract key insights, final result, and justification for this subproblem. Keep concise but complete.",
                context=attempt
            )

        # Solve subproblems in parallel, respecting dependencies
        solved_subproblems = {}
        for subproblem in subproblems:
            # Wait for dependencies if any
            deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
            deps = [d.strip() for d in deps if d.strip()]
            if deps:
                await asyncio.gather(*[asyncio.sleep(0) for dep in deps if dep in solved_subproblems])  # Simple dependency wait
            
            result = await solve_subproblem(subproblem)
            solved_subproblems[subproblem['id']] = result

        # Step 4: Synthesize subproblem solutions into final answer
        synthesis_context = "\n\n".join([f"Subproblem {id}: {result}" for id, result in solved_subproblems.items()])
        
        synthesized = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into a complete, coherent answer:
            {synthesis_context}
            
            Ensure all constraints from original problem are satisfied.
            Derive the final numerical answer (integer 000-999).
            If multiple answers possible, select the one best supported by reasoning.
            Show final derivation clearly.""",
            context=synthesis_context
        )

        # Step 5: Extract and format final answer
        final_answer = await self.revise(
            instruction="""Extract the final numerical answer as an integer between 000 and 999.
            - If answer is not an integer in this range, return 000
            - Justify why this is the correct final answer
            - Double-check against original problem constraints
            Format: Exactly three digits (e.g., 042, 123, 999)""",
            context=synthesized
        )

        # Step 6: Fallback - if answer not found, try direct computation
        if not re.search(r'\b\d{3}\b', final_answer):
            # Try programmer as last resort
            computed = await self.programmer(
                instruction=f"""Compute the final answer directly from the problem.
                Problem: {self.problem_text}
                Classification: {classification}
                Previous synthesis: {synthesized}
                
                Write Python code to calculate the answer as integer 000-999.
                Handle edge cases and validate result.""",
                context=synthesis_context,
                max_retries=3
            )
            
            final_answer = await self.revise(
                instruction="Extract exactly three-digit integer answer from computation. If none, return 000.",
                context=computed
            )

        # Ensure output is exactly three digits
        match = re.search(r'\b(\d{3})\b', final_answer)
        if match:
            return match.group(1)
        else:
            return "000"