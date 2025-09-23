# Workflow ID: limr_108_0
# Benchmark: limr
# Data Indices: [270, 45]

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
        
        # Step 1: Initial Problem Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and identify key components:
            - Classify the problem type (geometry, number theory, algebra, etc.)
            - Identify known variables and constraints
            - Highlight any special conditions or requirements
            - Suggest potential solution approaches""",
            context=""
        )
        
        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop an algebraic solution approach based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a geometric solution approach based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a combinatorial solution approach based on: {initial_analysis}",
                context=initial_analysis
            )
        )
        
        # Step 3: Refinement of Each Strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine the solution approach, ensuring logical consistency and accuracy",
                context=strategy
            ) for strategy in strategies]
        )
        
        # Step 4: Synthesis and Decision-Making
        best_solution = await self.ensemble(
            instruction="Evaluate and synthesize the refined strategies, selecting the most promising solution",
            contexts_list=refined_strategies
        )
        
        # Step 5: Iterative Refinement Loop
        for _ in range(3):  # Limit iterations to avoid excessive computation
            verification = await self.revise(
                instruction="Verify the solution for accuracy and completeness, identifying any errors or gaps",
                context=best_solution
            )
            if "error" in verification.lower():
                best_solution = await self.revise(
                    instruction=f"Address identified issues: {verification}",
                    context=best_solution
                )
            else:
                break
        
        # Step 6: Final Synthesis and Presentation
        final_answer = await self.summarize(
            instruction="Condense the solution into a clear and concise format, presenting the final answer",
            context=best_solution
        )
        
        return final_answer