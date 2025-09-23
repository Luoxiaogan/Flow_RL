# Workflow ID: limr_65_0
# Benchmark: limr
# Data Indices: [91, 100]

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

        # Step 1: Initial Analysis - Classify the problem and identify key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify the domain (geometry, number theory, combinatorics, etc.)
            2. Extract key variables, constraints, and relationships
            3. Determine the expected answer format (integer, fraction, etc.)
            Provide structured classification.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Develop a solution using algebraic methods. Include:
                - Step-by-step reasoning
                - All necessary calculations
                - Verification of intermediate results""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Develop a solution using geometric methods. Include:
                - Coordinate transformations if applicable
                - Vector analysis or trigonometric identities
                - Diagrams or visual reasoning steps""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Develop a solution using combinatorial methods. Include:
                - Counting principles
                - Probabilistic reasoning
                - Recursive relations if applicable""",
                context=initial_analysis
            )
        )

        # Step 3: Refinement - Improve and validate each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the following solution:
                {strategy}
                
                Ensure:
                - Logical consistency
                - Correct calculations
                - Clarity and completeness of explanation""",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Summarization - Condense key insights from each strategy
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Summarize the refined solution:
                {refined_strategy}
                
                Focus on:
                - Key steps and insights
                - Final result and confidence level""",
                context=refined_strategy
            ) for refined_strategy in refined_strategies]
        )

        # Step 5: Ensemble - Select the best solution or synthesize insights
        final_solution = await self.ensemble(
            instruction="""Evaluate the summarized solutions:
            - Assess correctness and completeness
            - Consider computational efficiency
            - Select the most robust and elegant approach
            If multiple solutions are valid, synthesize them into a unified answer.""",
            contexts_list=summaries
        )

        # Step 6: Final Verification - Double-check the selected solution
        verified_solution = await self.revise(
            instruction=f"""Verify the final solution:
            {final_solution}
            
            Ensure:
            - All steps are accurate
            - The answer matches the expected format
            - No logical gaps remain""",
            context=final_solution
        )

        return verified_solution