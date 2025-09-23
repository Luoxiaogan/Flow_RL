# Workflow ID: limr_11_0
# Benchmark: limr
# Data Indices: [63, 99]

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

        # STEP 1: CLASSIFY THE PROBLEM TYPE AND STRATEGIZE
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your analysis must include:
            1. Primary domain classification (Geometry, Number Theory, Algebra, Combinatorics, Calculus, Sequences, etc.)
            2. Secondary characteristics (e.g., "involves tangency conditions", "nested radicals", "Diophantine constraints")
            3. Required mathematical techniques (e.g., "coordinate geometry", "modular arithmetic", "generating functions")
            4. Expected answer format (e.g., "integer 000-999", "equation in standard form", "interval notation")
            5. Potential pitfalls or common errors (e.g., "extraneous solutions from squaring", "domain restrictions", "gcd normalization")
            6. Recommended solution strategies (at least 3 distinct approaches if applicable)
            
            Format your response as a structured JSON-like block with clear section headers.""",
            context=""
        )

        # STEP 2: GENERATE MULTIPLE SOLUTION STRATEGIES IN PARALLEL
        strategy_instructions = [
            """Develop a complete solution using ALGEBRAIC/ANALYTIC approach. 
            - Translate geometric conditions into equations
            - Use symbolic manipulation
            - Eliminate variables systematically
            - Derive final form with explicit coefficient constraints""",
            
            """Develop a complete solution using GEOMETRIC/TRANSFORMATIONAL approach.
            - Use properties of circles, tangency, homothety, or inversion
            - Leverage symmetry or coordinate transformations
            - Derive locus through geometric reasoning
            - Convert final geometric insight into algebraic form""",
            
            """Develop a complete solution using COMPUTATIONAL/NUMERICAL approach.
            - Set up parametric equations or constraints
            - Use substitution and elimination
            - Consider edge cases and boundary conditions
            - Output must match required format precisely"""
        ]

        # Launch parallel strategy explorations
        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # STEP 3: REVISE EACH ATTEMPT WITH STRICT VALIDATION
        revision_instructions = [
            f"""CRITICALLY REVISE this solution attempt:
            - Verify every algebraic step for sign errors and calculation mistakes
            - Confirm external/internal tangency conditions are correctly modeled
            - Ensure final equation is in form Pa² + Qb² + Ra + Sb + T = 0
            - Validate that P>0 and gcd(|P|,|Q|,|R|,|S|,|T|)=1
            - If coefficients not normalized, factor out gcd and adjust
            - Preserve mathematical rigor; do not approximate
            
            Original classification context:
            {classification}""",
            
            f"""CRITICALLY REVISE this solution attempt:
            - Check geometric assumptions for validity
            - Verify distance formulas and radius conditions
            - Ensure locus derivation accounts for all constraints
            - Convert to required algebraic form without loss of generality
            - Normalize coefficients as per problem requirements
            
            Original classification context:
            {classification}""",
            
            f"""CRITICALLY REVISE this solution attempt:
            - Validate computational logic and variable substitutions
            - Check for domain restrictions or undefined operations
            - Ensure output format matches exactly
            - Normalize coefficients and confirm gcd=1, P>0
            - Cross-validate with alternative methods if possible
            
            Original classification context:
            {classification}"""
        ]

        revised_attempts = await asyncio.gather(
            *[self.revise(instruction=instr, context=attempt) 
              for instr, attempt in zip(revision_instructions, strategy_attempts)]
        )

        # STEP 4: PROGRAMMATIC VALIDATION AND COEFFICIENT NORMALIZATION
        code_instructions = [
            """Write Python code that:
            1. Parses the derived equation from the solution
            2. Extracts coefficients P, Q, R, S, T
            3. Computes gcd of absolute values of all coefficients
            4. Divides all coefficients by gcd to normalize
            5. Ensures P is positive (multiply entire equation by -1 if needed)
            6. Outputs the final equation in required format
            7. Validates that all coefficients are integers and gcd=1
            
            Return the final normalized equation as string.""",
            
            """Write Python code that:
            1. Symbolically verifies the solution satisfies original tangency conditions
            2. Checks at least 3 test points on the derived locus
            3. Confirms internal/external tangency constraints hold
            4. Returns validation report and normalized equation""",
            
            """Write Python code that:
            1. Compares all derived solutions for consistency
            2. Identifies any discrepancies in coefficients
            3. Selects the most mathematically rigorous version
            4. Performs final gcd normalization and sign adjustment
            5. Returns the authoritative final answer"""
        ]

        code_validations = await asyncio.gather(
            *[self.programmer(instruction=instr, context=attempt) 
              for instr, attempt in zip(code_instructions, revised_attempts)]
        )

        # STEP 5: ENSEMBLE SYNTHESIS - COMBINE BEST ELEMENTS
        final_answer = await self.ensemble(
            instruction="""Synthesize the final answer by:
            1. Comparing all three code-validated solutions
            2. Selecting the most complete and rigorously derived version
            3. Incorporating any superior elements from alternatives (e.g., better normalization, clearer derivation)
            4. Ensuring absolute compliance with problem requirements: 
               - Integer coefficients
               - P positive
               - gcd(|P|,|Q|,|R|,|S|,|T|) = 1
               - Correct equation form
            5. Presenting ONLY the final equation in the specified format, nothing else""",
            contexts_list=code_validations
        )

        # STEP 6: FINAL VERIFICATION LOOP (up to 3 iterations)
        for iteration in range(3):
            verification = await self.generate(
                instruction=f"""FINAL VERIFICATION:
                Check this answer against ALL original problem constraints:
                - Does it represent the correct locus of centers?
                - Are coefficients integers? Is P positive? Is gcd=1?
                - Is the equation in exactly the form Pa² + Qb² + Ra + Sb + T = 0?
                - Does it satisfy both external tangency to C1 and internal tangency to C2?
                
                If any issues found, describe them specifically. If perfect, respond ONLY with "VALID".
                
                Current answer: {final_answer}""",
                context=final_answer
            )
            
            if "VALID" in verification:
                break
            else:
                # Revise based on verification feedback
                final_answer = await self.revise(
                    instruction=f"""FIX the following issues identified in verification:
                    {verification}
                    
                    Preserve all correct elements while correcting the specific errors noted.
                    Re-normalize coefficients if needed. Maintain required format strictly.""",
                    context=final_answer
                )
        else:
            # If loop exhausted, use ensemble one last time
            final_answer = await self.ensemble(
                instruction="Select the most reliable version from all attempts, prioritizing mathematical correctness and format compliance.",
                contexts_list=[final_answer] + list(code_validations)
            )

        return final_answer