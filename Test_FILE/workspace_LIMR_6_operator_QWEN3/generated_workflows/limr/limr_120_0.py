# Workflow ID: limr_120_0
# Benchmark: limr
# Data Indices: [345, 6]

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

        # Step 1: Problem Classification and Strategic Orientation
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategic orientation:
            1. Identify the apparent domain (geometry, algebra, combinatorics, number theory, etc.)
            2. Detect any hidden domains or red herrings (e.g., a geometry problem that is actually number theory)
            3. List 3-5 potential solution strategies ranked by likely effectiveness
            4. Flag any known traps, common mistakes, or counterintuitive elements
            5. Suggest whether decomposition is viable or if insight-based approaches are needed
            6. Recommend computational vs analytical emphasis
            Format as structured markdown with clear section headers.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition (if viable)
        decomposition = await self.decompose(
            instruction=f"""Based on classification:
            {classification}
            
            Decompose this problem into minimal solvable subproblems. For each:
            - Define the subproblem with mathematical precision
            - Specify input/output requirements
            - List dependencies (which subproblems must be solved first)
            - Indicate whether it requires computation, proof, or insight
            If decomposition is not viable (e.g., insight-driven problem), return a single subproblem describing the core insight needed.""",
            context=classification
        )

        # Step 3: Parallel Strategy Exploration
        # Generate 4 independent solution attempts using different mathematical lenses
        strategy_instructions = [
            """Approach as a pure algebraist: manipulate symbols, equations, and identities. 
            Focus on transformations, substitutions, and algebraic structures. 
            Derive step-by-step with full rigor. Assume nothing is obvious.""",
            
            """Approach as a geometer: use spatial reasoning, coordinate systems, or vector operations. 
            Draw mental diagrams. Look for symmetries, invariants, or geometric interpretations of algebraic entities. 
            Convert non-geometric elements into geometric ones if possible.""",
            
            """Approach as a combinatorialist: count, enumerate, or find bijections. 
            Look for hidden combinatorial structures, generating functions, or probabilistic interpretations. 
            Even if problem seems non-combinatorial, force a counting perspective.""",
            
            """Approach as a number theorist: focus on divisibility, modular arithmetic, prime structures, or Diophantine constraints. 
            Reduce modulo small primes. Look for integer constraints or hidden congruences. 
            Apply theorems like Fermat's Little Theorem or Chinese Remainder Theorem if applicable."""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{strategy_instructions[i]}
                
                Based on problem classification:
                {classification}
                
                And decomposition:
                {[f"Subproblem {sp['id']}: {sp['description']}" for sp in decomposition]}
                
                Develop a complete solution attempt. Show all steps. Box final answer. 
                If stuck, state why and suggest alternative angles.""",
                context=""
            ) for i in range(4)]
        )

        # Step 4: Iterative Refinement Loop
        refined_attempts = []
        for attempt in solution_attempts:
            current = attempt
            for refinement_round in range(2):  # Two refinement passes
                critique = await self.generate(
                    instruction=f"""Critique this solution with extreme skepticism:
                    - Check every logical step for gaps or assumptions
                    - Verify dimensional consistency and unit correctness
                    - Test boundary cases and edge conditions
                    - Look for arithmetic or algebraic errors
                    - Assess whether answer format (integer 000-999) is satisfied
                    - If error found, explain precisely where and why.
                    - If no error, strengthen the argument with additional verification.
                    Return structured critique with 'ERROR FOUND:' or 'VERIFIED:' prefix.""",
                    context=current
                )
                
                if "ERROR FOUND:" in critique:
                    current = await self.revise(
                        instruction=f"""Revise the solution to fix the error:
                        {critique}
                        
                        Preserve correct parts. Add missing rigor. Recompute if necessary.
                        Maintain step-by-step clarity. Box final answer.""",
                        context=current
                    )
                else:
                    break  # Break if verified
            refined_attempts.append(current)

        # Step 5: Ensemble Synthesis and Selection
        final_answer = await self.ensemble(
            instruction="""Synthesize the best elements from all solution attempts:
            1. Compare mathematical rigor, completeness, and correctness
            2. Prefer solutions that explicitly verify against problem constraints
            3. Favor solutions that acknowledge and avoid known traps
            4. Select the most elegant and efficient path
            5. Extract the final integer answer (000-999) and present it prominently
            6. If answers conflict, perform meta-analysis to resolve discrepancy
            7. Return ONLY the final integer answer as a 3-digit string (e.g., '123')""",
            contexts_list=refined_attempts
        )

        # Step 6: Final Validation and Formatting
        validated_answer = await self.programmer(
            instruction="""Extract and validate the final answer:
            - Input: Solution text containing a final answer
            - Task: Extract the integer answer between 000 and 999
            - Validate: Must be integer, must be in range, must appear as final conclusion
            - Format: Return exactly 3 digits as string (e.g., '042' not '42')
            - If multiple candidates, choose the one most consistently derived
            - If none valid, return '000' as fallback""",
            context=final_answer
        )

        # Clean extraction (in case programmer returns more than just the number)
        match = re.search(r'\b\d{3}\b', validated_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: try to extract any 1-3 digit number and pad
            match = re.search(r'\b\d{1,3}\b', validated_answer)
            if match:
                return match.group(0).zfill(3)
            else:
                return "000"  # Ultimate fallback