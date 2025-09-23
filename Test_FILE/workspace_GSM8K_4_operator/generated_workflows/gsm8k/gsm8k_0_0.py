# Workflow ID: gsm8k_0_0
# Benchmark: gsm8k
# Data Indices: [214, 19]

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

        # Step 1: Initial Analysis - Extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, units, relationships, and constraints from the problem. 
            Classify the problem type (e.g., sequential operations, rate problems, proportions). 
            Format the output as structured text with clear labels.""",
            context=""
        )

        # Step 2: Solution Planning - Generate solution strategies
        solution_strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the extracted information:
                {initial_analysis}
                
                Develop a step-by-step solution plan for solving the problem. 
                Ensure each step logically follows from the previous one.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Consider alternative approaches to solve the problem:
                {initial_analysis}
                
                Generate a different but valid solution strategy.""",
                context=initial_analysis
            )
        )

        # Step 3: Strategy Selection - Choose the best approach
        selected_strategy = await self.ensemble(
            instruction="Select the most reliable and efficient solution strategy.",
            contexts_list=solution_strategies
        )

        # Step 4: Execution - Solve the problem step-by-step
        steps = selected_strategy.split("\n")
        intermediate_results = []
        for i, step in enumerate(steps):
            if step.strip() == "":
                continue
            result = await self.generate(
                instruction=f"""Execute this step:
                {step}
                
                Use the following intermediate results if applicable:
                {intermediate_results}""",
                context=selected_strategy
            )
            intermediate_results.append(result)

        # Step 5: Final Validation - Critique and refine the final result
        final_result = intermediate_results[-1]
        validated_result = await self.revise(
            instruction=f"""Critique the final result:
            {final_result}
            
            Ensure it is numerically exact and meets the problem's requirements. 
            Revise if necessary.""",
            context=final_result
        )

        # Step 6: Return the Final Answer
        return validated_result.strip()