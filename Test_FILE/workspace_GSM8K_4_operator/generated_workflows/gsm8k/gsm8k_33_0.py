# Workflow ID: gsm8k_33_0
# Benchmark: gsm8k
# Data Indices: [192, 84]

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

        # Step 1: Initial Analysis - Extract key entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Identify all numbers and their units/contexts
            - List all entities (people, objects, etc.) and their relationships
            - Highlight what the problem is asking for
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies in Parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a step-by-step solution strategy based on:
                {initial_analysis}
                Focus on direct calculations and logical reasoning.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop an alternative solution strategy based on:
                {initial_analysis}
                Consider indirect methods or different interpretations.""",
                context=initial_analysis
            )
        )

        # Step 3: Ensemble Selection - Choose the best strategy
        selected_strategy = await self.ensemble(
            instruction="Select the most robust and efficient strategy.",
            contexts_list=strategies
        )

        # Step 4: Execute the Selected Strategy Step-by-Step
        steps = selected_strategy.split("\n")
        intermediate_results = []
        for step in steps:
            if "Calculate" in step or "Compute" in step:
                calculation_result = await self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    Show all intermediate steps and the final result.""",
                    context="\n".join(intermediate_results)
                )
                # Validate the result
                validation = await self.revise(
                    instruction=f"""Verify the correctness of:
                    {calculation_result}
                    Ensure all arithmetic is accurate and units are consistent.""",
                    context=calculation_result
                )
                if "error" in validation.lower():
                    revised_result = await self.revise(
                        instruction=f"""Correct the following calculation:
                        {calculation_result}
                        Based on validation feedback: {validation}""",
                        context=calculation_result
                    )
                    intermediate_results.append(revised_result)
                else:
                    intermediate_results.append(calculation_result)

        # Step 5: Final Synthesis - Condense into a single numerical answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the intermediate results.",
            context="\n".join(intermediate_results)
        )

        return final_answer.strip()