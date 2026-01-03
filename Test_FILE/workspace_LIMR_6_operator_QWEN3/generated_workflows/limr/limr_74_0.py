# Workflow ID: limr_74_0
# Benchmark: limr
# Data Indices: [16, 286]

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

        # PHASE 1: META-ANALYSIS & STRATEGY IDENTIFICATION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this mathematical problem. Identify:
            1. The primary mathematical domain (algebra, geometry, combinatorics, number theory, trigonometry, etc.)
            2. Key entities: variables, constants, functions, constraints
            3. Required output format and constraints (e.g., integer between 000-999)
            4. Potential solution strategies ranked by likelihood of success
            5. Any hidden symmetries, transformations, or non-obvious insights
            6. Known theorems or identities that might apply
            Present as a structured report with clear sections.""",
            context=""
        )

        # PHASE 2: ADAPTIVE DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal solvable subproblems. For each:
            - Define precisely what needs to be computed or proven
            - Specify dependencies (which subproblems must be solved first)
            - Suggest the most appropriate mathematical tool or technique
            - Estimate difficulty and risk of error
            Prioritize subproblems that are independent and can be solved in parallel.""",
            context=problem_analysis
        )

        # PHASE 3: PARALLEL STRATEGY EXPLORATION
        # Generate 3 distinct solution approaches based on analysis
        strategy_instructions = [
            """Assume an ALGEBRAIC approach. Focus on:
            - Polynomial manipulation, factoring, equation solving
            - Variable substitution, symmetry exploitation
            - Exact symbolic computation
            Derive step-by-step solution leading to integer answer.""",
            
            """Assume a NUMBER THEORETIC / COMBINATORIAL approach. Focus on:
            - Modular arithmetic, divisibility, prime factors
            - Counting principles, combinatorial identities
            - Integer constraints and Diophantine reasoning
            Derive step-by-step solution leading to integer answer.""",
            
            """Assume a FUNCTIONAL / TRANSFORMATIVE approach. Focus on:
            - Trigonometric identities, complex numbers, generating functions
            - Problem reformulation via substitution or coordinate change
            - Exploiting periodicity, symmetry, or asymptotic behavior
            Derive step-by-step solution leading to integer answer."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_analysis) for instr in strategy_instructions]
        )

        # PHASE 4: VALIDATION & REFINEMENT
        validated_attempts = []
        for i, attempt in enumerate(strategy_attempts):
            # First revision: fix logical gaps and add rigor
            refined = await self.revise(
                instruction=f"""Critically review this solution attempt #{i+1}:
                - Verify each mathematical step for correctness
                - Flag any unjustified assumptions
                - Ensure all constraints from original problem are satisfied
                - Confirm the final answer is an integer between 000-999
                - Improve clarity and add missing justifications
                If fundamental flaws exist, propose corrected approach.""",
                context=attempt
            )
            
            # Second revision: computational verification if applicable
            computationally_checked = await self.revise(
                instruction="""If this solution involves numerical computation:
                - Extract the key computation needed
                - Verify it can be executed precisely (no floating point errors)
                - If uncertain, propose using programmer operator for exact calculation
                If no computation needed, confirm symbolic derivation is watertight.""",
                context=refined
            )
            validated_attempts.append(computationally_checked)

        # PHASE 5: SYNTHESIS & FINAL ANSWER EXTRACTION
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all solution attempts:
            - Identify which approach(es) are mathematically sound
            - Resolve any contradictions between approaches
            - Combine insights if multiple approaches contribute partial solutions
            - Produce a single unified solution with complete reasoning
            - Extract the final integer answer (000-999) and box it as \boxed{answer}
            Prioritize solutions that are fully justified and match problem constraints.""",
            contexts_list=validated_attempts
        )

        # PHASE 6: FINAL VERIFICATION & OUTPUT FORMATTING
        final_answer = await self.revise(
            instruction="""Extract and verify the final answer:
            1. Locate the boxed integer answer in the solution
            2. Confirm it satisfies all problem constraints
            3. Validate it's between 000 and 999
            4. If multiple answers exist, select the one best supported by reasoning
            5. Output ONLY the integer in the format: \boxed{123}
            If no valid answer found, return \boxed{000} as fallback.""",
            context=synthesized_solution
        )

        # Extract just the boxed answer using regex as final safeguard
        match = re.search(r'\\boxed\{(\d{1,3})\}', final_answer)
        if match:
            answer = match.group(1).zfill(3)  # Ensure 3-digit format
            return f"\\boxed{{{answer}}}"
        else:
            # Fallback if extraction fails
            return "\\boxed{000}"