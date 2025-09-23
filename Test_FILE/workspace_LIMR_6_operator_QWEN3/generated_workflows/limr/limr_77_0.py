# Workflow ID: limr_77_0
# Benchmark: limr
# Data Indices: [121, 80]

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

        # PHASE 1: Problem Decomposition & Classification
        decomposition = await self.decompose(
            instruction="""Break this mathematical problem into atomic, solvable subproblems.
            For each subproblem:
            - State what needs to be calculated or proven
            - Identify required inputs and formulas
            - Note dependencies on other subproblems
            - Flag any ambiguous or missing information
            Structure output as numbered subproblems with dependency mapping.""",
            context=""
        )

        classification = await self.generate(
            instruction=f"""Analyze the problem through multiple mathematical lenses:
            1. Primary domain (geometry, algebra, combinatorics, number theory, etc.)
            2. Required techniques (proof, calculation, optimization, counting, etc.)
            3. Key mathematical entities (shapes, sequences, functions, probabilities, etc.)
            4. Potential solution strategies (formula application, transformation, enumeration, etc.)
            5. Known pitfalls or non-obvious insights
            Format as a structured analysis with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Exploration
        # Generate 3 distinct solution approaches based on classification
        approach_instructions = [
            f"""Develop a solution using {classification.split('1. Primary domain')[1].split('2.')[0].strip()} techniques.
            Focus on direct application of domain-specific formulas and theorems.
            Show all steps explicitly and justify each mathematical operation.""",
            
            f"""Develop a solution using computational or algorithmic reasoning.
            Translate the problem into a series of calculations or logical steps that could be programmed.
            Focus on precision and edge case handling.""",
            
            f"""Develop a solution using combinatorial or probabilistic reasoning if applicable, 
            otherwise use geometric or algebraic transformation.
            Look for non-obvious symmetries, patterns, or reformulations that simplify the problem."""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in approach_instructions]
        )

        # PHASE 3: Refinement & Verification
        refined_solutions = []
        for i, attempt in enumerate(solution_attempts):
            refined = await self.revise(
                instruction=f"""Critically evaluate and improve this solution:
                - Verify mathematical correctness of each step
                - Check for missing edge cases or assumptions
                - Ensure all variables are defined and constraints respected
                - Improve clarity and logical flow
                - Confirm final answer format (integer 000-999)
                If fundamental flaws exist, propose corrected approach.""",
                context=attempt
            )
            # Attempt computational verification if applicable
            try:
                computed = await self.programmer(
                    instruction=f"""Implement a Python solution to verify the mathematical result.
                    Extract key calculations from this solution:
                    {refined}
                    Return only the final integer answer (000-999) or 'ERROR' if computation fails.""",
                    context=refined,
                    max_retries=2
                )
                # Append computational result to refined solution for ensemble
                refined_solutions.append(f"{refined}\n\nCOMPUTATIONAL_VERIFICATION: {computed}")
            except:
                refined_solutions.append(refined)

        # PHASE 4: Synthesis & Final Answer Extraction
        synthesized = await self.ensemble(
            instruction="""Synthesize the best elements from all solution attempts:
            1. Identify consensus answers or overlapping conclusions
            2. Resolve contradictions through mathematical rigor
            3. Select the most complete and verified solution
            4. Extract the final integer answer (000-999)
            5. If no consensus, create a hybrid solution combining strongest elements
            Output format: Final Answer: [integer] followed by brief justification.""",
            contexts_list=refined_solutions
        )

        # PHASE 5: Final Verification & Formatting
        final_answer = await self.programmer(
            instruction=f"""Extract and verify the final integer answer from this synthesis:
            {synthesized}
            Rules:
            - Answer must be an integer between 000 and 999
            - If multiple answers, select the one with strongest verification
            - If no valid answer, return 000
            - Return ONLY the 3-digit integer (e.g., "123")""",
            context=synthesized,
            max_retries=1
        )

        # Clean and validate final output
        match = re.search(r'\b\d{1,3}\b', final_answer)
        if match:
            answer = int(match.group())
            return f"{answer:03d}"
        else:
            # Fallback: extract any number from synthesis
            match = re.search(r'\b\d{1,3}\b', synthesized)
            if match:
                answer = int(match.group())
                return f"{answer:03d}"
            else:
                return "000"