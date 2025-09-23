# Workflow ID: limr_52_0
# Benchmark: limr
# Data Indices: [194, 10]

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
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Classify the problem type (geometry, number theory, etc.)
            - Extract key variables, equations, and constraints
            - Identify relationships and dependencies
            Provide a structured breakdown.""",
            context=""
        )
        
        # Step 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a solution using algebraic methods:
                - Solve equations
                - Factorize polynomials
                - Apply transformations
                Context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a solution using combinatorial methods:
                - Count possibilities
                - Use generating functions
                - Explore recursive sequences
                Context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a solution using geometric methods:
                - Analyze shapes and figures
                - Apply coordinate geometry
                - Use trigonometric identities
                Context: {analysis}""",
                context=analysis
            )
        )
        
        # Step 3: Intermediate Validation
        validated_strategies = []
        for strategy in strategies:
            validation = await self.generate(
                instruction=f"""Validate the following solution:
                - Check for errors
                - Verify adherence to constraints
                - Ensure logical consistency
                Solution: {strategy}""",
                context=strategy
            )
            if "error" not in validation.lower():
                validated_strategies.append(strategy)
            else:
                revised_strategy = await self.revise(
                    instruction=f"""Revise the solution to address issues:
                    - Fix errors
                    - Clarify reasoning
                    - Add missing details
                    Issues: {validation}""",
                    context=strategy
                )
                validated_strategies.append(revised_strategy)
        
        # Step 4: Synthesis and Selection
        best_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Evaluate computational efficiency
            - Assess clarity and correctness
            - Choose the most promising approach""",
            contexts_list=validated_strategies
        )
        
        # Step 5: Iterative Refinement
        refined_solution = best_solution
        for _ in range(3):  # Limit iterations to avoid infinite loops
            refinement = await self.revise(
                instruction=f"""Refine the solution:
                - Improve clarity
                - Optimize calculations
                - Ensure precision
                Current solution: {refined_solution}""",
                context=refined_solution
            )
            if refinement == refined_solution:  # No further changes
                break
            refined_solution = refinement
        
        # Step 6: Final Output
        final_answer = await self.summarize(
            instruction="""Extract the final answer:
            - Ensure it is an integer between 000 and 999
            - Format correctly
            Solution: {refined_solution}""",
            context=refined_solution
        )
        
        return final_answer