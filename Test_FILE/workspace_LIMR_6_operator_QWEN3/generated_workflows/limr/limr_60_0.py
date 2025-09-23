# Workflow ID: limr_60_0
# Benchmark: limr
# Data Indices: [228, 186]

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

        # STEP 1: META-CLASSIFICATION - Understand problem archetype
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify primary domain: complex analysis, geometry, combinatorics, number theory, algebra, optimization, sequences.
            2. List applicable theorems, identities, or standard techniques for this domain.
            3. Flag any non-obvious transformations or substitutions that might simplify the problem.
            4. Predict potential pitfalls or common mistakes in this problem type.
            5. Propose a high-level solution strategy with 3-5 key milestones.
            Output in structured markdown with clear section headers.""",
            context=""
        )

        # STEP 2: STRATEGIC DECOMPOSITION - Break into solvable subproblems
        subproblems = await self.decompose(
            instruction=f"""Decompose based on classification:
            Classification: {classification}
            
            Create atomic, sequentially dependent subproblems. Each should:
            - Be solvable independently given its dependencies
            - Have a clear success criterion (what constitutes 'solved')
            - Include necessary mathematical tools or theorems
            - Anticipate where computational verification might be needed
            
            Prioritize decomposition that reveals hidden structure or symmetry.""",
            context=classification
        )

        # STEP 3: PARALLEL SOLUTION EXPLORATION - Generate multiple approaches
        solution_attempts = []
        approach_instructions = [
            """Adopt an ALGEBRAIC approach: Focus on symbolic manipulation, equation transformation, and identity application. 
            Express everything in terms of fundamental operations. Avoid geometric or combinatorial interpretations unless essential.
            Show every algebraic step with justification.""",
            
            """Adopt a GEOMETRIC/VISUAL approach: Interpret the problem spatially. Use diagrams, coordinate systems, or vector representations.
            Look for symmetries, invariants, or proportional relationships. Translate non-geometric elements into spatial analogs.""",
            
            """Adopt a COMPUTATIONAL/NUMERICAL approach: Identify where exact computation is needed. Set up equations for programming solution.
            Determine variables, constraints, and objective functions. Prepare for symbolic or exact fractional output."""
        ]

        # Generate parallel solution attempts
        attempt_tasks = []
        for i, approach_instr in enumerate(approach_instructions):
            task = self.generate(
                instruction=f"""{approach_instr}

                Context from classification: {classification[:1000]}  # Truncated for context length
                
                Solve the problem using this specific lens. If the approach is fundamentally unsuitable, explain why and pivot to 
                the most relevant alternative while maintaining the core strategy of this approach.""",
                context=""
            )
            attempt_tasks.append(task)
        
        raw_attempts = await asyncio.gather(*attempt_tasks)

        # STEP 4: RIGOROUS REVISION - Correct and deepen each attempt
        revised_attempts = []
        for i, attempt in enumerate(raw_attempts):
            revised = await self.revise(
                instruction=f"""Perform logical and mathematical audit:
                - Verify every equation, inequality, and transformation
                - Check domain restrictions, division by zero, undefined operations
                - Ensure all variables are properly constrained
                - Confirm theorem applications are valid (cite specific theorems)
                - Fill any gaps in reasoning with explicit justifications
                - If solution is incomplete, extend it to full resolution
                - Maintain exact symbolic form - no decimal approximations
                
                Target: Airtight, graduate-level mathematical proof or derivation.""",
                context=attempt
            )
            revised_attempts.append(revised)

        # STEP 5: SYNTHESIS & CONSENSUS - Merge best elements
        synthesized = await self.ensemble(
            instruction="""Synthesize a definitive solution:
            1. Compare all solution attempts for mathematical soundness and completeness
            2. Identify points of agreement - these form the core of the final solution
            3. Resolve contradictions by appealing to first principles and theorem validity
            4. Incorporate the most elegant or insightful steps from each attempt
            5. Structure as a coherent, step-by-step proof with clear logical flow
            6. Highlight any non-obvious insights or clever transformations used
            7. Explicitly state the final answer in boxed format as required""",
            contexts_list=revised_attempts
        )

        # STEP 6: COMPUTATIONAL VERIFICATION (if applicable)
        # Check if problem requires exact computation
        needs_computation = await self.generate(
            instruction=f"""Determine if final answer requires programmatic computation:
            Analyze the synthesized solution: {synthesized[:800]}
            
            Return ONLY 'YES' if the answer requires exact numerical computation that benefits from code execution,
            or 'NO' if the answer is purely symbolic or already computable by hand. Be conservative - only say YES if 
            computation is truly necessary for exact fractional/integer result.""",
            context=synthesized
        )

        final_answer = synthesized
        if "YES" in needs_computation.upper():
            computation = await self.programmer(
                instruction=f"""Execute precise computation:
                Based on this mathematical derivation: {synthesized[:1500]}
                
                Write Python code to compute the exact final answer. Requirements:
                - Use fractions or symbolic math if needed
                - Avoid floating point - maintain exact precision
                - Return answer as integer between 000-999
                - If answer is fractional, compute exact numerator/denominator
                - Output should be the integer answer only, no explanations""",
                context=synthesized
            )
            # Extract just the numerical result
            final_answer = await self.generate(
                instruction=f"""Extract and format final answer:
                From this computational result: {computation}
                And this mathematical derivation: {synthesized[:1000]}
                
                Extract the exact integer answer between 000-999. If multiple candidates exist, 
                choose the one consistent with mathematical derivation. Format as 3-digit string 
                with leading zeros if necessary. Output ONLY the 3-digit number, nothing else.""",
                context=f"{synthesized}\n\nCOMPUTATION: {computation}"
            )

        # STEP 7: FINAL VALIDATION & FORMATTING
        validated_answer = await self.revise(
            instruction="""Final verification and formatting:
            1. Confirm answer is an integer between 000 and 999
            2. Verify it matches the problem's requirements and constraints
            3. Ensure no calculation errors or logical inconsistencies remain
            4. Format as exactly 3 digits with leading zeros if needed
            5. Output ONLY the 3-digit string, nothing else - no explanations, no units, no text
            
            Example outputs: "042", "789", "001" """,
            context=final_answer
        )

        # Extract just the 3-digit answer using regex to be safe
        match = re.search(r'\b\d{3}\b', validated_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: try to extract any number and format to 3 digits
            numbers = re.findall(r'\d+', validated_answer)
            if numbers:
                num = int(numbers[0]) % 1000  # Ensure in range
                return f"{num:03d}"
            else:
                return "000"  # Ultimate fallback