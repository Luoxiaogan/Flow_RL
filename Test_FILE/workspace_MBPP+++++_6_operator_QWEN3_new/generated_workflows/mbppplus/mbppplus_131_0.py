# Workflow ID: mbppplus_131_0
# Benchmark: mbppplus
# Data Indices: [164, 69]

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

        # Phase 1: Problem Classification & Strategy Selection
        classification = await self.generate(
            instruction="""Analyze the problem and classify it with high precision:
            1. Determine the primary domain: mathematical, logical, structural (lists/strings), or algorithmic.
            2. Identify the core operation: transformation, validation, search, aggregation, or pattern recognition.
            3. Infer hidden constraints from examples: input types, output types, edge behaviors.
            4. Assess if the reference solution (if any) is reliable or potentially misleading.
            5. Recommend a primary and backup solution strategy.
            Format your response as a structured JSON-like outline.""",
            context=""
        )

        # Phase 2: Problem Decomposition
        subproblems = await self.decompose(
            instruction="""Break this problem into atomic, solvable subproblems. For each:
            - Define what must be computed or decided
            - Specify any dependencies on other subproblems
            - Note potential edge cases specific to this subproblem
            Prioritize subproblems that handle type safety, empty inputs, and boundary conditions first.""",
            context=classification
        )

        # Phase 3: Parallel Solution Generation & Edge Case Synthesis
        solution_task = self.generate(
            instruction=f"""Generate 3 distinct solution approaches based on classification:
            {classification}

            Approach 1: Literal - closely follow reference solution if available.
            Approach 2: Abstract - derive general formula or invariant.
            Approach 3: Defensive - include type checks, edge case handling, and input validation.
            
            For each, output complete Python function with correct signature and imports.""",
            context=""
        )

        edge_case_task = self.generate(
            instruction=f"""Generate 5-7 high-risk edge cases not shown in examples:
            - Consider empty inputs, single elements, duplicates, negatives, zeros, maxima/minima
            - For sequences: reversed, sorted, constant, singleton, empty
            - For numbers: 0, 1, negative, very large, floating point if applicable
            - Format as Python assert statements.""",
            context=classification
        )

        solutions, edge_cases = await asyncio.gather(solution_task, edge_case_task)

        # Phase 4: Solution Validation & Iterative Refinement
        solution_list = re.split(r'\n\s*={5,}\s*\n', solutions)  # Split by separator lines
        validated_solutions = []

        for i, candidate in enumerate(solution_list[:3]):  # Limit to 3 candidates
            if not candidate.strip():
                continue
                
            # Test against generated edge cases
            validation = await self.programmer(
                instruction=f"""Execute this candidate solution against these edge cases:
                {edge_cases}
                
                Return ONLY the function code if all tests pass. If any fail, return 'FAILED' followed by error details.""",
                context=candidate,
                max_retries=1
            )
            
            if "FAILED" not in validation:
                validated_solutions.append(validation)
            else:
                # One revision attempt
                revised = await self.revise(
                    instruction=f"""Fix the solution to handle these failures:
                    {validation}
                    
                    Preserve function signature. Add necessary edge case handling.
                    Return complete corrected function.""",
                    context=candidate
                )
                # Quick retest
                retest = await self.programmer(
                    instruction=f"""Re-test with same edge cases:
                    {edge_cases}""",
                    context=revised,
                    max_retries=1
                )
                if "FAILED" not in retest:
                    validated_solutions.append(revised)

        # Phase 5: Ensemble Selection
        if len(validated_solutions) == 0:
            # Fallback: take first generated solution
            final_solution = solution_list[0] if solution_list else solutions
        elif len(validated_solutions) == 1:
            final_solution = validated_solutions[0]
        else:
            final_solution = await self.ensemble(
                instruction="""Select the optimal solution based on:
                1. Correctness (must pass all edge cases)
                2. Robustness (handles widest range of inputs)
                3. Simplicity (fewest assumptions, cleanest logic)
                4. Type safety (matches expected signature)
                Return ONLY the selected function code.""",
                contexts_list=validated_solutions
            )

        # Phase 6: Final Hardening & Signature Compliance
        hardened = await self.revise(
            instruction="""Final hardening pass:
            1. Ensure function signature exactly matches requirement (parameter names, return type)
            2. Add missing imports if any
            3. Handle empty/None inputs explicitly if not already
            4. Remove any debug prints or extra outputs
            5. Return ONLY the clean, production-ready function code.""",
            context=final_solution
        )

        return hardened