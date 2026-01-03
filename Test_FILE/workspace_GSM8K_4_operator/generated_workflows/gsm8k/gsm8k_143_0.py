# Workflow ID: gsm8k_143_0
# Benchmark: gsm8k
# Data Indices: [206, 52]

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
        
        # Initial analysis to extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Extract and classify key information:
            - Identify all numerical values and their context
            - Determine the problem type (sequential, rate, distribution, proportion, multi-entity)
            - Highlight what the question is asking for
            - Note any specific constraints or conditions""",
            context=""
        )
        
        # Generate multiple solution attempts using different strategies
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Attempt 1: Direct Calculation
                Using the extracted information: {initial_analysis}
                Solve the problem step-by-step with precise calculations.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt 2: Logical Deduction
                Using the extracted information: {initial_analysis}
                Solve the problem through logical reasoning and deduction.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt 3: Estimation
                Using the extracted information: {initial_analysis}
                Estimate the solution using approximations and verify the result.""",
                context=initial_analysis
            )
        )
        
        # Validate and refine each solution attempt
        refined_solutions = []
        for attempt in solution_attempts:
            validated = await self.revise(
                instruction=f"""Validate and refine the solution:
                - Check for calculation errors
                - Ensure logical consistency
                - Verify intermediate results
                - Improve clarity and precision""",
                context=attempt
            )
            refined_solutions.append(validated)
        
        # Ensemble decision to select the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Evaluate accuracy and reliability
            - Consider intermediate results and validation feedback
            - Choose the most precise and logically consistent solution""",
            contexts_list=refined_solutions
        )
        
        # Extract the final numerical answer
        final_answer = await self.generate(
            instruction=f"""Extract the final answer:
            From the selected solution: {final_solution}
            Identify and present the final numerical answer only.""",
            context=final_solution
        )
        
        return final_answer.strip()