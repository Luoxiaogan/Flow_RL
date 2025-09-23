# Workflow ID: limr_68_0
# Benchmark: limr
# Data Indices: [218, 136]

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

        # STEP 1: META-COGNITIVE PROBLEM ANALYSIS
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your analysis must include:
            1. Problem Type Classification: Identify if this is primarily combinatorial, algebraic, geometric, number-theoretic, recursive, probabilistic, or optimization-based. Note if it's hybrid.
            2. Solution Paradigm Prediction: What mathematical tools are likely required? (e.g., modular arithmetic, generating functions, coordinate geometry, inclusion-exclusion, recurrence solving)
            3. Key Constraints & Invariants: What conditions must hold? What quantities are conserved or bounded?
            4. Expected Answer Characteristics: Is the answer likely to be small? Does it have special properties (prime, power of 2, etc.)?
            5. Potential Pitfalls: What are common mistakes or subtle assumptions in problems like this?
            6. Strategic Recommendations: Suggest 2-3 distinct high-level approaches to try.
            Format your response as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION BRANCHING (DIAMOND PATTERN)
        # Generate three distinct solution approaches based on analysis
        approach_instructions = [
            f"""Based on this analysis: {problem_analysis}
            Develop a DETAILED solution using a COMBINATORIAL/ENUMERATIVE approach. 
            - Systematically count cases or construct possibilities
            - Use combinatorial identities if applicable
            - Consider symmetry and overcounting corrections
            - Show step-by-step reasoning with clear justifications""",
            
            f"""Based on this analysis: {problem_analysis}
            Develop a DETAILED solution using an ALGEBRAIC/ANALYTICAL approach.
            - Set up equations, recurrences, or functional relationships
            - Apply algebraic manipulations, substitutions, or transformations
            - Solve symbolically before plugging in numbers
            - Verify domain constraints and solution validity""",
            
            f"""Based on this analysis: {problem_analysis}
            Develop a DETAILED solution using a COMPUTATIONAL/SIMULATION approach.
            - Design an algorithm or simulation that models the problem
            - Consider edge cases and boundary conditions
            - If exact computation is infeasible, use smart enumeration or mathematical shortcuts
            - Document your computational strategy clearly"""
        ]

        solution_attempts = await asyncio.gather(
            self.generate(instruction=approach_instructions[0], context=""),
            self.generate(instruction=approach_instructions[1], context=""),
            self.generate(instruction=approach_instructions[2], context="")
        )

        # STEP 3: ADVERSARIAL VALIDATION (CRITIQUE BRANCHES)
        critique_tasks = []
        for i, attempt in enumerate(solution_attempts):
            critique = self.generate(
                instruction=f"""CRITICALLY EVALUATE this solution attempt:
                {attempt}
                
                Your task:
                1. Identify any logical gaps, calculation errors, or unjustified assumptions
                2. Construct a minimal counterexample if the solution is flawed
                3. Check boundary conditions and edge cases
                4. Verify that the final answer format matches requirements (integer 000-999)
                5. Rate confidence in this solution (1-10) and explain why
                Be brutally honest — your goal is to break this solution if possible.""",
                context=attempt
            )
            critique_tasks.append(critique)
        
        critiques = await asyncio.gather(*critique_tasks)

        # STEP 4: ENSEMBLE SYNTHESIS WITH CONFIDENCE WEIGHTING
        synthesis = await self.ensemble(
            instruction="""Synthesize the best elements from all solution attempts and their critiques. Your task:
            1. Compare all three solutions and their critiques side-by-side
            2. Identify which approach has the highest confidence rating and fewest flaws
            3. If one solution is clearly superior, select it and incorporate fixes from its critique
            4. If multiple solutions agree, synthesize a unified answer with combined reasoning
            5. If all solutions have flaws, design a NEW hybrid approach that avoids their pitfalls
            6. Output the FINAL ANSWER as an integer between 000 and 999, clearly boxed at the end
            7. Include a confidence assessment (High/Medium/Low) based on critique consensus""",
            contexts_list=[f"Solution {i+1}:\n{sol}\n\nCritique {i+1}:\n{crit}" 
                          for i, (sol, crit) in enumerate(zip(solution_attempts, critiques))]
        )

        # STEP 5: CONFIDENCE-AWARE REFINEMENT LOOP
        confidence_check = await self.generate(
            instruction=f"""Evaluate the confidence level of this synthesized solution:
            {synthesis}
            
            Respond with ONLY ONE WORD: 'HIGH', 'MEDIUM', or 'LOW'""",
            context=synthesis
        )

        final_answer = synthesis
        if "MEDIUM" in confidence_check.upper() or "LOW" in confidence_check.upper():
            # Trigger refinement: decompose and re-solve with programmer assistance
            decomposition = await self.decompose(
                instruction=f"""Based on this analysis: {problem_analysis}
                and this low-confidence synthesis: {synthesis}
                Break the problem into atomic, computationally verifiable subproblems.
                Each subproblem should be solvable independently and contribute directly to the final answer.
                Prioritize subproblems that can be validated with code.""",
                context=synthesis
            )
            
            # Solve subproblems in parallel with programmer where applicable
            subproblem_solutions = []
            for sub in decomposition:
                if any(keyword in sub['description'].lower() for keyword in ['compute', 'calculate', 'enumerate', 'simulate', 'count']):
                    # Use programmer for computational subproblems
                    sub_solution = await self.programmer(
                        instruction=f"""Solve this subproblem: {sub['description']}
                        Write efficient, correct Python code that computes the exact answer.
                        Include comments explaining your approach.
                        Handle edge cases and validate your result.""",
                        context=problem_analysis
                    )
                else:
                    # Use generate for conceptual subproblems
                    sub_solution = await self.generate(
                        instruction=f"""Solve this subproblem: {sub['description']}
                        Provide rigorous mathematical reasoning.
                        Reference relevant theorems or principles.
                        Show all steps clearly.""",
                        context=problem_analysis
                    )
                subproblem_solutions.append(sub_solution)
            
            # Re-synthesize with subproblem solutions
            final_answer = await self.ensemble(
                instruction="""Integrate all subproblem solutions into a complete, verified answer.
                1. Combine results logically
                2. Cross-validate between subproblems
                3. Ensure consistency with original problem constraints
                4. Output FINAL ANSWER as integer 000-999, boxed
                5. Include final confidence assessment""",
                contexts_list=subproblem_solutions
            )

        # STEP 6: FINAL SUMMARIZATION AND ANSWER EXTRACTION
        final_summary = await self.summarize(
            instruction="""Extract the final numerical answer and create a concise verification report.
            1. Locate the boxed integer answer (000-999) in the solution
            2. If multiple candidates exist, select the one with highest confidence
            3. Verify it satisfies all problem constraints
            4. Output ONLY the integer answer (no text, no units, no explanation)
            Example: 427""",
            context=final_answer
        )

        return final_summary