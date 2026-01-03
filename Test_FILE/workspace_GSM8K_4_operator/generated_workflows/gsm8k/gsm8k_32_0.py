# Workflow ID: gsm8k_32_0
# Benchmark: gsm8k
# Data Indices: [247, 106]

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

        # Step 1: Extract key information
        extraction = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem.
            Format the output as a structured list:
            - Entities: [names and roles]
            - Numbers: [values and what they represent]
            - Relationships: [how entities and numbers are connected]""",
            context=""
        )

        # Step 2: Classify problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {extraction}
            
            Categories:
            1. Sequential Operations
            2. Rate Problems
            3. Distribution
            4. Proportions
            5. Multi-entity Tracking
            
            Provide a clear classification and reasoning.""",
            context=extraction
        )

        # Step 3: Generate multiple solution attempts in parallel
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using a step-by-step approach.
                Classification: {classification}
                Extracted Info: {extraction}
                
                Show all intermediate steps and calculations.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Solve the problem using a proportional reasoning approach.
                Classification: {classification}
                Extracted Info: {extraction}
                
                Focus on ratios, percentages, and scaling.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Solve the problem using a distribution-based approach.
                Classification: {classification}
                Extracted Info: {extraction}
                
                Divide quantities, handle remainders, and ensure fairness.""",
                context=extraction
            )
        )

        # Step 4: Refine each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the solution by verifying calculations and improving clarity.
                Solution: {sol}""",
                context=sol
            ) for sol in solutions]
        )

        # Step 5: Summarize each refined solution
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Summarize the solution concisely.
                Refined Solution: {refined}""",
                context=refined
            ) for refined in refined_solutions]
        )

        # Step 6: Ensemble to select the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Numerical accuracy
            - Logical consistency
            - Clarity of presentation""",
            contexts_list=summaries
        )

        # Step 7: Extract the final numerical answer
        answer = await self.generate(
            instruction=f"""Extract the final numerical answer from the selected solution.
            Final Solution: {final_solution}
            
            Ensure the answer is precise and formatted correctly.""",
            context=final_solution
        )

        return answer