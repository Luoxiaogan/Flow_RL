# Workflow ID: limr_85_0
# Benchmark: limr
# Data Indices: [174, 108]

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

        # STEP 1: INITIAL CLASSIFICATION & COMPLEXITY ASSESSMENT
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify the primary mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            2. List all mathematical objects involved (equations, functions, sets, geometric figures, etc.)
            3. Determine if the problem requires exact computation, proof, counting, or optimization
            4. Assess complexity on scale 1-5 (1=trivial, 5=extremely complex) based on:
               - Number of non-obvious insights required
               - Depth of prerequisite knowledge
               - Length of solution chain
            5. Recommend initial decomposition strategy based on complexity.
            Output in structured JSON-like format with keys: domain, objects, requirement, complexity, strategy.""",
            context=""
        )

        # STEP 2: ADAPTIVE DECOMPOSITION
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem using strategy: {classification}
            Create subproblems that:
            - Are mathematically independent where possible
            - Build prerequisite knowledge before advanced steps
            - Include at least one 'verification' subproblem for critical steps
            - Flag any step requiring non-obvious insight or transformation
            Output as list of subproblem dictionaries with clear dependencies.""",
            context=classification
        )

        # STEP 3: PARALLEL STRATEGY GENERATION (DIAMOND PATTERN)
        strategy_instructions = [
            """Approach 1: Direct Symbolic Manipulation
            - Apply algebraic identities, modular arithmetic rules, or calculus techniques as appropriate
            - Show every transformation step with justification
            - Reduce expressions to simplest form before final computation""",
            
            """Approach 2: Algorithmic/Computational Solution
            - Design a step-by-step algorithm that could be implemented in code
            - Identify key variables, loops, and termination conditions
            - Consider edge cases and boundary conditions explicitly""",
            
            """Approach 3: Geometric/Visual or Combinatorial Interpretation
            - Even if problem appears algebraic, seek geometric representation or combinatorial model
            - Look for symmetry, invariants, or counting principles
            - Transform problem into equivalent but more intuitive form"""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # STEP 4: ADVERSARIAL REVISION (CRITIQUE EACH ATTEMPT)
        critiques = await asyncio.gather(
            *[self.revise(
                instruction=f"""Adversarial Critique:
                Assume this solution is WRONG. Find the flaw.
                - Check arithmetic and algebraic manipulations step by step
                - Verify all assumptions and domain constraints
                - Test edge cases and boundary conditions
                - If no flaw found, provide rigorous proof of correctness
                - Output must be: [VERIFIED] or [FLAWED: description]""",
                context=attempt
            ) for attempt in strategy_attempts]
        )

        # STEP 5: SYNTHETIC ENSEMBLE (MERGE VERIFIED COMPONENTS)
        ensemble_result = await self.ensemble(
            instruction="""Synthesize final answer:
            1. From all strategy attempts, extract only components marked [VERIFIED]
            2. If multiple verified answers exist, check for consistency
            3. If inconsistency exists, resolve by:
               - Preferring solutions with explicit verification steps
               - Running additional modular checks
               - Cross-validating with alternative methods
            4. Derive final integer answer between 000-999
            5. Include brief justification tracing back to original problem constraints""",
            contexts_list=critiques
        )

        # STEP 6: PROGRAMMATIC VERIFICATION (WHERE APPLICABLE)
        # Only proceed if problem involves computation/counting
        if any(keyword in classification.lower() for keyword in ["compute", "count", "number of", "find how many"]):
            verification_code = await self.programmer(
                instruction=f"""Generate Python code to verify the answer:
                - Implement the core mathematical logic from the problem
                - Include all constraints and boundary conditions
                - Output only the final integer result (no explanations)
                - If answer is single digit or two digits, format as 3-digit with leading zeros
                Context: {ensemble_result}""",
                context=ensemble_result
            )
            # Extract numerical result from code output
            code_result = await self.generate(
                instruction=f"""Extract the final 3-digit integer from this code output:
                {verification_code}
                If multiple numbers, select the one matching the problem's expected answer format.
                If no clear answer, default to ensemble result but flag for manual review.""",
                context=verification_code
            )
            final_candidate = code_result
        else:
            final_candidate = ensemble_result

        # STEP 7: FINAL SANITY CHECK & FORMATTING
        final_answer = await self.revise(
            instruction="""Final Answer Preparation:
            1. Extract the numerical answer from the text
            2. Verify it is an integer between 000 and 999
            3. If outside range, re-examine solution for error
            4. Format as exactly 3 digits with leading zeros (e.g., 5 becomes 005, 42 becomes 042)
            5. Remove ALL text, explanations, units, or symbols
            6. Output ONLY the 3-digit integer, nothing else""",
            context=final_candidate
        )

        # STEP 8: ULTIMATE VALIDATION (ENSURE IT SATISFIES ORIGINAL PROBLEM)
        validation = await self.generate(
            instruction=f"""Ultimate Validation:
            Given the original problem and this answer: {final_answer}
            - Substitute the answer back into the original problem statement
            - Verify all conditions and constraints are satisfied
            - If any condition fails, output [INVALID] and explain why
            - If all conditions pass, output [VALID] followed by the 3-digit answer
            Original problem: {self.problem_text}""",
            context=final_answer
        )

        # Extract final 3-digit answer
        match = re.search(r'\b\d{3}\b', validation)
        if match:
            return match.group(0)
        else:
            # Fallback: return first 3-digit number found or pad if single number
            numbers = re.findall(r'\d+', validation)
            if numbers:
                num = int(numbers[0])
                if 0 <= num <= 999:
                    return f"{num:03d}"
            # Last resort: return 000 (should never happen in well-formed problems)
            return "000"