# Workflow ID: limr_78_0
# Benchmark: limr
# Data Indices: [238, 264]

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

        # Step 1: Initial Analysis - Extract key components and classify the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem to identify:
            - Key variables and constants
            - Mathematical domain (geometry, number theory, etc.)
            - Constraints and conditions
            - Expected answer format
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Solve the problem using algebraic methods. Show all steps.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Solve the problem using geometric reasoning. Include diagrams if applicable.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Solve the problem using combinatorial or probabilistic methods. Highlight assumptions.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation Loop - Critique and refine each approach
        refined_approaches = []
        for approach in approaches:
            refined = await self.revise(
                instruction=f"""Critique this solution:
                - Check for logical consistency
                - Verify calculations
                - Ensure adherence to constraints
                If issues are found, correct them.""",
                context=approach
            )
            refined_approaches.append(refined)

        # Step 4: Synthesis - Combine insights from all paths
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the refined approaches:
            - Select the most rigorous and complete solution
            - Resolve any discrepancies between approaches
            - Present the final answer in the required format.""",
            contexts_list=refined_approaches
        )

        return final_solution