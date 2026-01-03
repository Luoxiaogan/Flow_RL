# Workflow ID: limr_93_0
# Benchmark: limr
# Data Indices: [106, 211]

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

        # Step 1: Strategic Problem Decomposition & Classification
        decomposition = await self.decompose(
            instruction="""Break down this mathematical problem into its core conceptual components. Identify:
            1. The primary mathematical domain (algebra, combinatorics, geometry, number theory, etc.)
            2. Key variables, constraints, and relationships
            3. Potential solution strategies or known problem archetypes it resembles
            4. Any symmetries, invariants, or transformations that might simplify the problem
            5. The expected form of the answer (integer, expression, etc.)
            Structure your output as a clear, hierarchical breakdown with labeled sections.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration
        # Generate three distinct solution approaches based on decomposition
        strategy_instructions = [
            """Develop a solution approach focusing on ALGEBRAIC MANIPULATION and SYMBOLIC REASONING. 
            Look for substitutions, factorizations, or transformations that simplify the problem. 
            Pay special attention to nested expressions, radicals, or functional equations. 
            Show all steps clearly and justify each transformation mathematically.""",
            
            """Develop a solution approach focusing on COMBINATORIAL or COUNTING PRINCIPLES. 
            Even if the problem doesn't appear combinatorial at first, consider whether it can be 
            reframed as a counting problem, probability question, or arrangement with constraints. 
            Use principles like inclusion-exclusion, generating functions, or casework where appropriate.""",
            
            """Develop a solution approach focusing on GEOMETRIC or VISUAL INTERPRETATION. 
            Consider whether the problem can be represented geometrically, using coordinates, 
            vectors, or spatial reasoning. Look for distance formulas, symmetry, or optimization 
            in geometric space that might provide insight."""
        ]

        # Launch parallel solution attempts
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=str(decomposition)) 
              for instr in strategy_instructions]
        )

        # Step 3: Iterative Refinement of Each Solution Attempt
        refined_attempts = []
        for attempt in solution_attempts:
            current = attempt
            for refinement_round in range(3):  # Up to 3 refinement passes
                critique = await self.generate(
                    instruction=f"""Critically evaluate this solution attempt:
                    1. Are all steps mathematically justified?
                    2. Are there any logical gaps or unwarranted assumptions?
                    3. Does the final answer match the expected format (integer 000-999)?
                    4. Are there edge cases or special conditions not considered?
                    5. Is the reasoning clear and complete?
                    Provide specific, actionable feedback for improvement.""",
                    context=current
                )
                
                # If critique indicates no major issues, break early
                if "no issues" in critique.lower() or "correct" in critique.lower():
                    break
                    
                # Otherwise, revise based on critique
                current = await self.revise(
                    instruction=f"""Improve this solution based on the following critique:
                    {critique}
                    
                    Specifically:
                    - Fill any logical gaps identified
                    - Correct any mathematical errors
                    - Ensure all steps are clearly justified
                    - Verify the final answer format
                    - Consider any edge cases mentioned""",
                    context=current
                )
            refined_attempts.append(current)

        # Step 4: Summarize Each Refined Attempt for Ensemble Processing
        summarized_attempts = await asyncio.gather(
            *[self.summarize(
                instruction="""Extract the core insight and final answer from this solution attempt.
                Structure your summary as:
                CORE INSIGHT: [The key mathematical insight or transformation]
                SOLUTION STEPS: [Brief outline of critical steps]
                FINAL ANSWER: [The numerical answer, if any, in format ###]
                If no clear answer is reached, state 'INCOMPLETE'""",
                context=attempt
            ) for attempt in refined_attempts]
        )

        # Step 5: Ensemble Synthesis - Combine Best Insights
        final_synthesis = await self.ensemble(
            instruction="""Synthesize the best elements from these solution attempts into a single, 
            rigorous, complete solution. Consider:
            1. Which approach provides the most elegant and correct path to the solution?
            2. Can insights from multiple approaches be combined for a more robust solution?
            3. Is there consensus on the final answer? If not, which answer is best justified?
            4. Ensure the final solution includes all necessary steps and justifications.
            5. The answer must be an integer between 000 and 999.
            Produce a polished, complete solution with clear reasoning and boxed final answer.""",
            contexts_list=summarized_attempts
        )

        # Step 6: Computational Verification (if applicable)
        # Extract potential answer for verification
        answer_verification = await self.programmer(
            instruction="""Extract the final numerical answer from the solution and verify it computationally.
            If the problem involves equations, plug the answer back to verify.
            If combinatorial, compute the value directly if feasible.
            If geometric, verify with coordinate calculations.
            Return the verified answer or note any discrepancies.""",
            context=final_synthesis,
            max_retries=3
        )

        # Step 7: Final Self-Verification and Formatting
        final_answer = await self.revise(
            instruction="""Perform final verification and formatting:
            1. Ensure the answer is an integer between 000 and 999
            2. Confirm all steps are mathematically sound
            3. Format the answer as \boxed{###} at the end
            4. Remove any extraneous text, keeping only the essential solution and boxed answer
            5. If multiple answers are possible, ensure all are considered and the correct one selected""",
            context=f"{final_synthesis}\n\nCOMPUTATIONAL VERIFICATION:\n{answer_verification}"
        )

        return final_answer