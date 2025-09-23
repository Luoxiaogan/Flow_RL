# Workflow ID: limr_23_0
# Benchmark: limr
# Data Indices: [111, 257]

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

        # STEP 1: DIAGNOSE - Structured mathematical triage
        diagnosis = await self.generate(
            instruction="""Perform a deep mathematical diagnosis of this problem. Output a JSON-like structure with:
            1. "domain": Primary mathematical domain (e.g., "number theory", "combinatorics", "algebra", "geometry", "optimization")
            2. "key_objects": List of critical mathematical objects (variables, functions, shapes, sequences)
            3. "constraints": Explicit and implicit constraints (equations, inequalities, modular conditions, bounds)
            4. "solution_approaches": List of 3-5 plausible solution strategies with brief rationale
            5. "answer_format": Expected answer type (integer, fraction, proof, etc.)
            6. "complexity_estimate": Low/Medium/High based on steps and insight required
            Be precise, structured, and exhaustive.""",
            context=""
        )

        # STEP 2: STRATEGY GENERATION - Create parallel solution threads
        strategy_list = await self.generate(
            instruction=f"""Based on this diagnosis:
            {diagnosis}
            
            Generate 4 distinct solution strategies. For each, provide:
            - Strategy name (e.g., "Modular Arithmetic Approach")
            - Core mathematical technique
            - Step-by-step plan (3-5 steps)
            - Potential pitfalls or edge cases
            Format as numbered list with clear section headers.""",
            context=diagnosis
        )

        # STEP 3: PARALLEL EXECUTION - Launch independent solution threads
        async def execute_strategy(strategy_desc: str, index: int) -> str:
            # Generate initial solution attempt
            draft = await self.generate(
                instruction=f"""Implement this strategy:
                {strategy_desc}
                
                Requirements:
                - Show all mathematical steps clearly
                - Justify non-obvious insights
                - Maintain precision (no approximations)
                - Box final answer if numerical
                - If stuck, explain why and suggest alternatives""",
                context=strategy_desc
            )
            
            # Revise for rigor and completeness
            refined = await self.revise(
                instruction="""Improve this solution:
                - Fill any logical gaps
                - Add missing justifications
                - Verify calculations
                - Ensure answer matches required format
                - Highlight any remaining uncertainties""",
                context=draft
            )
            
            # Computational verification if applicable
            try:
                verified = await self.programmer(
                    instruction=f"""Verify the solution computationally:
                    - Implement key calculations
                    - Test edge cases
                    - Validate final answer
                    - If symbolic, check with sample values
                    Return code and output.""",
                    context=refined,
                    max_retries=2
                )
                return f"{refined}\n\n--- COMPUTATIONAL VERIFICATION ---\n{verified}"
            except:
                return refined  # Proceed without verification if code fails

        # Extract individual strategies and run in parallel
        strategies = [s.strip() for s in strategy_list.split('\n\n') if s.strip() and s[0].isdigit()]
        solution_attempts = await asyncio.gather(
            *[execute_strategy(strategy, i) for i, strategy in enumerate(strategies[:4])],
            return_exceptions=True
        )

        # Filter out any failed attempts
        valid_attempts = [str(attempt) for attempt in solution_attempts if not isinstance(attempt, Exception)]

        if not valid_attempts:
            # Fallback: direct generation if all parallel attempts failed
            return await self.generate(
                instruction="Solve this problem directly with maximum rigor and detail.",
                context=""
            )

        # STEP 4: ENSEMBLE - Synthesize best solution
        final_solution = await self.ensemble(
            instruction="""Select and synthesize the best solution:
            Criteria:
            1. Mathematical rigor (complete proofs, justified steps)
            2. Computational verification (if applicable)
            3. Clarity and precision
            4. Handling of edge cases
            5. Alignment with problem constraints
            If multiple solutions are valid, merge their strongest elements.
            Present final answer in required format (typically integer 000-999).""",
            contexts_list=valid_attempts
        )

        # STEP 5: CRITIQUE & FINAL REVISION
        critique = await self.generate(
            instruction=f"""Critically evaluate this solution:
            {final_solution}
            
            Specifically check:
            - Logical consistency
            - Computational accuracy
            - Boundary condition handling
            - Answer format compliance
            - Potential alternative interpretations
            List any concerns or suggested improvements.""",
            context=final_solution
        )

        # Final polish
        polished = await self.revise(
            instruction=f"""Incorporate this critique:
            {critique}
            
            Produce the final, flawless solution:
            - Address all concerns raised
            - Ensure perfect clarity
            - Verify answer format
            - Include only essential steps
            - Present final answer prominently""",
            context=final_solution
        )

        # STEP 6: ULTIMATE VERIFICATION (if answer is numerical)
        if any(char.isdigit() for char in polished):
            try:
                verification_code = await self.generate(
                    instruction=f"""Generate Python code to verify the final numerical answer in this solution:
                    {polished}
                    
                    Code should:
                    - Recompute the answer independently
                    - Test edge cases
                    - Output only the final integer answer (000-999 format)
                    - Include assertions for critical steps""",
                    context=polished
                )
                
                verified_answer = await self.programmer(
                    instruction="Execute verification code and return only the final answer.",
                    context=verification_code,
                    max_retries=3
                )
                
                # If verification succeeds, append it
                if verified_answer and any(c.isdigit() for c in verified_answer):
                    return f"{polished}\n\n--- VERIFIED ANSWER ---\n{verified_answer}"
            except:
                pass  # Proceed with polished solution if verification fails

        return polished