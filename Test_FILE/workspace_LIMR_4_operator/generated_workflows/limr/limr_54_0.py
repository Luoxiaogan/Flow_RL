# Workflow ID: limr_54_0
# Benchmark: limr
# Data Indices: [89, 124]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the problem type (geometry, number theory, etc.)
            - Extract key entities, relationships, and constraints
            - Highlight any special cases or conditions
            - Suggest potential solution strategies""",
            context=""
        )

        # Step 2: Parallel Solution Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop solution using algebraic manipulation:
                {initial_analysis}
                - Show all steps explicitly
                - Maintain precision throughout""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop solution using geometric reasoning:
                {initial_analysis}
                - Use diagrams or coordinate systems if applicable
                - Ensure logical consistency""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop solution using combinatorial methods:
                {initial_analysis}
                - Apply counting principles or probability rules
                - Verify calculations""",
                context=initial_analysis
            )
        )

        # Step 3: Synthesize Best Approach
        synthesized_solution = await self.ensemble(
            instruction="""Select or combine the best solution:
            - Evaluate each approach for correctness and clarity
            - Combine complementary insights if necessary
            - Ensure the final solution adheres to problem constraints""",
            contexts_list=strategies
        )

        # Step 4: Iterative Refinement
        refined_solution = synthesized_solution
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {refined_solution}
                - Check for errors or inconsistencies
                - Confirm adherence to constraints
                - Suggest improvements if needed""",
                context=refined_solution
            )
            if "error" in validation.lower() or "improve" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution based on validation:
                    {validation}
                    - Address identified issues
                    - Improve clarity and precision""",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Verification and Summarization
        final_verification = await self.revise(
            instruction=f"""Ensure the solution is complete and correct:
            {refined_solution}
            - Double-check all calculations
            - Confirm logical consistency
            - Format the answer appropriately""",
            context=refined_solution
        )
        final_answer = await self.summarize(
            instruction="""Condense the solution into a concise format:
            - Include only essential information
            - Present the final answer clearly""",
            context=final_verification
        )

        return final_answer