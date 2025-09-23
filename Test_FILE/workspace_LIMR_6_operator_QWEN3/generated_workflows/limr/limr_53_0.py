# Workflow ID: limr_53_0
# Benchmark: limr
# Data Indices: [281, 241]

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

        # Step 1: Meta-Analysis - Understand the problem's mathematical nature
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem:
            1. Classify by domain: Is this primarily algebra, number theory, combinatorics, geometry, or probability?
            2. Identify all given quantities, unknowns, and constraints.
            3. List relevant theorems, identities, or standard techniques that might apply (e.g., Vieta's formulas, modular arithmetic, combinatorial identities).
            4. Propose three distinct high-level solution strategies, each with estimated difficulty and potential pitfalls.
            5. Flag any ambiguities, tricks, or non-standard interpretations in the problem statement.
            6. Predict whether the solution will require symbolic manipulation, numerical computation, or combinatorial enumeration.
            Format your response as a structured report with clear section headings.""",
            context=""
        )

        # Step 2: Conditional Branch - Check if direct computation is needed (e.g., base conversion, large arithmetic)
        computation_check = await self.generate(
            instruction="""Based on the following analysis, determine if this problem can be solved primarily through direct computation or algorithmic implementation:
            - Does it involve base conversion, large number arithmetic, iterative processes, or explicit enumeration?
            - Would a short Python script be sufficient to compute the answer?
            Answer with ONLY "YES" or "NO".""",
            context=problem_analysis
        )

        if "YES" in computation_check.upper():
            # Direct computation path
            code_solution = await self.programmer(
                instruction=f"""Write a Python script to solve this problem based on the analysis:
                {problem_analysis}
                
                Requirements:
                - The script must compute the exact integer answer between 000 and 999.
                - Include comments explaining the mathematical logic.
                - Handle edge cases if any.
                - Print only the final integer answer, nothing else.
                - Do not use external libraries beyond standard Python.""",
                context=problem_analysis
            )
            final_answer = code_solution
        else:
            # Step 3: Parallel Solution Sketches - Explore multiple mathematical approaches
            sketch_instructions = [
                """Develop a solution sketch using ALGEBRAIC manipulation:
                - Express all relationships as equations.
                - Use substitution, elimination, or polynomial identities.
                - Track variable dependencies carefully.
                - Show intermediate steps but don't worry about final polish.
                - Flag any assumptions made.""",
                
                """Develop a solution sketch using COMBINATORIAL or NUMBER THEORETIC reasoning:
                - Look for counting principles, modular patterns, or divisibility rules.
                - Consider generating functions, recursive relations, or prime factorizations.
                - Use combinatorial identities if applicable.
                - Show case analysis if needed.
                - Flag any assumptions made.""",
                
                """Develop a solution sketch using GEOMETRIC or FUNCTIONAL transformation:
                - If geometric, assign coordinates or use vector properties.
                - If algebraic, consider symmetry, substitution, or function properties.
                - Transform the problem into an equivalent but simpler form.
                - Show transformation steps clearly.
                - Flag any assumptions made."""
            ]

            # Generate parallel sketches
            sketch_tasks = [
                self.generate(instruction=instr, context=problem_analysis)
                for instr in sketch_instructions
            ]
            initial_sketches = await asyncio.gather(*sketch_tasks)

            # Step 4: Revise each sketch for errors and gaps
            revision_tasks = [
                self.revise(
                    instruction="""Critically review this solution sketch:
                    - Verify logical consistency of each step.
                    - Check for arithmetic or algebraic errors.
                    - Identify any unjustified assumptions or leaps in reasoning.
                    - Suggest specific improvements or corrections.
                    - If a step is unclear, propose a clearer alternative.
                    - Preserve the original approach but enhance its rigor.""",
                    context=sketch
                )
                for sketch in initial_sketches
            ]
            revised_sketches = await asyncio.gather(*revision_tasks)

            # Step 5: Ensemble - Synthesize the best insights into a unified solution
            synthesized_solution = await self.ensemble(
                instruction="""Synthesize a final, rigorous solution from these revised sketches:
                - Identify which parts of each sketch are correct and insightful.
                - Resolve any contradictions between approaches.
                - Combine the strongest elements into a single coherent solution.
                - Fill any remaining gaps with additional reasoning.
                - Ensure every step is justified and leads logically to the answer.
                - The final answer must be an integer between 000 and 999.
                - Present the solution in clear, step-by-step mathematical prose.""",
                contexts_list=revised_sketches
            )

            # Step 6: Adversarial Validation - Try to break the solution
            adversarial_check = await self.generate(
                instruction="""Play devil's advocate: Assume this solution is incorrect.
                - What is the most likely error or oversight?
                - Can you construct a counterexample or alternative interpretation?
                - Are there boundary cases or special conditions not considered?
                - If you find a credible flaw, describe it precisely.
                - If no flaw is found, state 'SOLUTION VALIDATED'.""",
                context=synthesized_solution
            )

            # Step 7: Final revision based on adversarial feedback
            if "SOLUTION VALIDATED" not in adversarial_check.upper():
                final_answer = await self.revise(
                    instruction=f"""Revise the solution to address the following critique:
                    {adversarial_check}
                    
                    - Correct any identified errors.
                    - Strengthen any weak points.
                    - Ensure the final answer is an integer between 000 and 999.
                    - Output only the final integer answer, nothing else.""",
                    context=synthesized_solution
                )
            else:
                final_answer = synthesized_solution

        # Step 8: Extract and format final answer (ensure it's a clean integer)
        clean_answer = await self.revise(
            instruction="""Extract the final numerical answer from this solution:
            - The answer must be an integer between 000 and 999.
            - Remove all explanatory text, units, or formatting.
            - If multiple numbers are present, select the one that matches the problem's requirements.
            - If no clear answer is found, return '000'.
            - Output ONLY the three-digit integer, padded with leading zeros if necessary (e.g., '042', '123', '999').""",
            context=final_answer
        )

        # Final safety check: ensure output is a 3-digit integer
        match = re.search(r'\b\d{1,3}\b', clean_answer)
        if match:
            answer_int = int(match.group())
            if 0 <= answer_int <= 999:
                return f"{answer_int:03d}"
        
        # Fallback
        return "000"