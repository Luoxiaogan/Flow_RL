# Workflow ID: limr_95_0
# Benchmark: limr
# Data Indices: [74, 238]

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

        # Step 1: Initial problem analysis and strategy generation
        initial_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Identify:
            1. The mathematical domain(s) involved (algebra, geometry, number theory, combinatorics, etc.)
            2. Key variables, constraints, and what is being asked
            3. Any hidden assumptions or implicit constraints
            4. Three potential solution strategies, ranked by apparent feasibility
            5. Potential pitfalls or common mistakes to avoid
            Format your response with clear section headers for each of these points.""",
            context=""
        )

        # Step 2: Generate creative insights and non-obvious approaches
        creative_insights = await self.generate(
            instruction="""Based on the problem analysis, generate three non-obvious mathematical insights or transformations that could simplify or solve this problem. Consider:
            - Symmetry exploitation
            - Variable substitutions
            - Theorem applications (e.g., modular arithmetic, geometric properties)
            - Problem restatements in different mathematical domains
            - Clever algebraic manipulations
            For each insight, explain why it might be useful and how it could be applied.""",
            context=initial_analysis
        )

        # Step 3: Parallel strategy exploration
        # Generate three different solution approaches in parallel
        strategy_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a complete solution using Strategy 1 from the initial analysis:
                {initial_analysis}
                
                Incorporate any relevant insights from:
                {creative_insights}
                
                Show all steps clearly, justify key decisions, and verify intermediate results against problem constraints.""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a complete solution using Strategy 2 from the initial analysis:
                {initial_analysis}
                
                Incorporate any relevant insights from:
                {creative_insights}
                
                Show all steps clearly, justify key decisions, and verify intermediate results against problem constraints.""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a complete solution using Strategy 3 from the initial analysis:
                {initial_analysis}
                
                Incorporate any relevant insights from:
                {creative_insights}
                
                Show all steps clearly, justify key decisions, and verify intermediate results against problem constraints.""",
                context=""
            )
        )

        # Step 4: Summarize each approach for ensemble comparison
        summarized_approaches = []
        for i, approach in enumerate(strategy_attempts):
            summary = await self.summarize(
                instruction=f"""Summarize this solution approach #{i+1}:
                - Core strategy in one sentence
                - Key mathematical steps
                - Critical assumptions made
                - Potential weaknesses or uncertainties
                - Final answer (if reached)
                Keep summary under 200 words but preserve all essential information.""",
                context=approach
            )
            summarized_approaches.append(summary)

        # Step 5: Ensemble to select best approach or synthesize
        best_approach = await self.ensemble(
            instruction="""Evaluate these solution approaches and select the most reliable one, or synthesize a hybrid solution. Consider:
            - Mathematical rigor and completeness
            - Adherence to all problem constraints
            - Clarity and verifiability of steps
            - Plausibility of final answer
            - Handling of edge cases or special conditions
            If one approach is clearly superior, select it. If multiple have complementary strengths, create a synthesized solution that combines the best elements.
            Justify your selection or synthesis with specific references to the strengths and weaknesses of each approach.""",
            contexts_list=summarized_approaches
        )

        # Step 6: Attempt computational verification if applicable
        try:
            computational_verification = await self.programmer(
                instruction=f"""Based on the selected solution approach:
                {best_approach}
                
                Write Python code to computationally verify the solution. This could involve:
                - Direct calculation of the answer
                - Checking constraints are satisfied
                - Testing edge cases
                - Verifying intermediate steps
                If the problem is not amenable to computational verification, return 'NOT APPLICABLE'.""",
                context=best_approach,
                max_retries=2
            )
            
            # Integrate computational results if successful
            if "NOT APPLICABLE" not in computational_verification and "ERROR" not in computational_verification:
                best_approach = await self.revise(
                    instruction=f"""Integrate the computational verification results:
                    {computational_verification}
                    
                    Update your solution to reflect any corrections or additional confidence from the computational verification. 
                    If the computation contradicts your solution, revise accordingly. 
                    If it confirms your solution, add the computational evidence as additional support.""",
                    context=best_approach
                )
        except Exception:
            # Fallback if programmer fails
            pass

        # Step 7: Final revision for answer extraction and formatting
        final_answer = await self.revise(
            instruction="""Extract the final numerical answer from the solution. The answer must be:
            - An integer between 000 and 999
            - Explicitly stated and boxed if possible
            - Verified against all problem constraints
            - Formatted as a three-digit number (e.g., 042 for 42)
            
            If the answer is not in the correct format or range, revise the solution to correct this.
            If multiple answers are possible, select the one that best satisfies all constraints.
            If no valid answer can be determined, state this clearly.
            
            Your output should be ONLY the three-digit answer (e.g., "042"), nothing else.""",
            context=best_approach
        )

        # Step 8: Final validation and cleanup
        # Ensure output is clean three-digit format
        cleaned_answer = re.sub(r'\D', '', final_answer)
        if len(cleaned_answer) == 1:
            cleaned_answer = "00" + cleaned_answer
        elif len(cleaned_answer) == 2:
            cleaned_answer = "0" + cleaned_answer
        elif len(cleaned_answer) > 3:
            cleaned_answer = cleaned_answer[-3:]  # Take last 3 digits as fallback

        return cleaned_answer