# Workflow ID: limr_148_0
# Benchmark: limr
# Data Indices: [140, 225]

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

        # === PHASE 1: DEEP CLASSIFICATION & STRATEGY SELECTION ===
        classification = await self.generate(
            instruction="""Perform a deep structural classification of this problem. Answer the following in structured format:
            1. Problem Type: Is this primarily algebraic, geometric, combinatorial, number-theoretic, probabilistic, or optimization?
            2. Key Entities: List all variables, sequences, functions, or geometric objects involved.
            3. Constraints: What explicit or implicit constraints govern the solution?
            4. Expected Answer: What form must the answer take? (e.g., integer, modulo, count, time format)
            5. Solution Approach: Suggest 2-3 viable high-level strategies (e.g., 'recurrence relation', 'modular arithmetic', 'coordinate geometry', 'generating functions').
            6. Computational Need: Does this require symbolic manipulation (proof/algebra) or numerical computation (calculation/iteration)?
            7. Edge Cases: What boundary conditions or special cases must be considered?
            Be exhaustive and precise. This classification will guide all subsequent steps.""",
            context=""
        )

        # === PHASE 2: PARALLEL HYPOTHESIS GENERATION ===
        # Generate 3 distinct solution approaches based on classification
        approach_instructions = [
            """Using an ALGEBRAIC/ANALYTIC approach: 
            - Derive equations or identities from first principles.
            - Manipulate symbolically; avoid numerical substitution until final step.
            - Track variable dependencies and invariants.
            - Show all steps leading to the answer.""",
            
            """Using a COMPUTATIONAL/ALGORITHMIC approach:
            - Translate the problem into a step-by-step algorithm.
            - Identify loops, recursions, or iterative processes.
            - Prepare specifications for code implementation if needed.
            - Handle edge cases explicitly.""",
            
            """Using a COMBINATORIAL/STRUCTURAL approach:
            - Look for counting principles, bijections, or symmetry.
            - Consider generating functions, recursive decompositions, or probabilistic methods.
            - Exploit problem structure (e.g., sequences, graphs, arrangements)."""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(
                instruction=f"""{instr}

                Base your approach on this classification:
                {classification}

                Develop a complete, self-contained solution attempt. Be detailed and rigorous.""",
                context=""
            ) for instr in approach_instructions]
        )

        # === PHASE 3: STRATEGY ROUTING & ENHANCEMENT ===
        # Check if problem is computational → route to Programmer
        if "numerical computation" in classification.lower() or "calculation" in classification.lower():
            # Generate precise code specification
            code_spec = await self.generate(
                instruction=f"""Based on the following solution hypothesis, generate a precise Python code specification:
                - Define inputs and outputs clearly.
                - Specify data types and constraints.
                - Handle edge cases identified in classification.
                - Return final answer as integer between 000-999.

                Hypothesis:
                {hypotheses[1]}  # Computational hypothesis

                Output ONLY the specification in clear, imperative language.""",
                context=hypotheses[1]
            )
            
            # Execute code
            computation_result = await self.programmer(
                instruction=f"""Implement and execute the following specification:
                {code_spec}

                Ensure all edge cases are handled. Return only the final integer result.""",
                context=code_spec,
                max_retries=3
            )
            
            # Integrate computational result into hypotheses
            hypotheses.append(f"PROGRAMMER RESULT:\n{computation_result}")
        
        # === PHASE 4: SYNTHESIS & VALIDATION ===
        synthesized = await self.ensemble(
            instruction="""Synthesize the most reliable solution from the following attempts. Prioritize:
            1. Logical consistency and completeness.
            2. Alignment with problem constraints and classification.
            3. Handling of edge cases.
            4. Numerical precision (if applicable).
            If contradictions exist, resolve them by selecting the most mathematically sound approach. 
            Output a single, unified, polished solution.""",
            contexts_list=hypotheses
        )

        # Validate and revise (max 2 iterations)
        current_solution = synthesized
        for _ in range(2):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                - Check for logical gaps or unsupported assumptions.
                - Verify calculations (if any) step by step.
                - Confirm edge cases are addressed.
                - Ensure answer format matches requirements (integer 000-999).
                If no issues, output 'VALID'. Otherwise, list all flaws concisely.""",
                context=current_solution
            )
            
            if "VALID" in validation:
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix the following issues:
                    {validation}

                    Maintain all correct parts. Only modify flawed sections. Be precise.""",
                    context=current_solution
                )

        # === PHASE 5: FINAL EXTRACTION & FORMATTING ===
        final_answer = await self.generate(
            instruction="""Extract the final answer from the solution below. Rules:
            - Answer MUST be an integer between 000 and 999.
            - If multiple candidates exist, pick the one consistent with ALL constraints.
            - Format as exactly THREE digits, zero-padded (e.g., '042', '123', '007').
            - Do NOT include units, explanations, or text — ONLY the three-digit string.

            Solution:
            """ + current_solution,
            context=current_solution
        )

        # Clean and return
        # Extract exactly 3 digits
        match = re.search(r'\b(\d{3})\b', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: take last 3 digits if any number found
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                return numbers[-1][-3:].zfill(3)
            else:
                return "000"  # Ultimate fallback