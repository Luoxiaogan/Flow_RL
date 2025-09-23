# Workflow ID: gsm8k_47_0
# Benchmark: gsm8k
# Data Indices: [105, 102]

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

        # Step 1: Initial Analysis - Extract key information and structure
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Extract all numbers and their associated units/contexts
            - Identify relationships and dependencies between entities
            - Determine what the question is asking for
            - Note any constraints or conditions
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop a step-by-step solution strategy focusing on arithmetic operations:\n{initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a solution strategy using proportional reasoning:\n{initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a solution strategy using rate-based calculations:\n{initial_analysis}",
                context=initial_analysis
            )
        )

        # Step 3: Ensemble Decision - Choose the best strategy
        chosen_strategy = await self.ensemble(
            instruction="Evaluate and select the most effective solution strategy based on clarity, completeness, and feasibility.",
            contexts_list=strategies
        )

        # Step 4: Iterative Refinement - Validate and refine the chosen strategy
        refined_solution = chosen_strategy
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"Validate the solution steps: {refined_solution}\nCheck for errors and missing details.",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Correct the identified issues: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Summarize Final Answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the refined solution, ensuring it is precise and correctly formatted.",
            context=refined_solution
        )

        return final_answer.strip()