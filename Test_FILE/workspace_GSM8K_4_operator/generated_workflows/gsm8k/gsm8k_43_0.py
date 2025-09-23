# Workflow ID: gsm8k_43_0
# Benchmark: gsm8k
# Data Indices: [191, 69]

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
        
        # Step 1: Extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Extract all numbers, entities, and relationships from the problem. 
            Classify the problem type (e.g., rate, distribution, proportion). 
            Identify what is being asked for and any constraints.""",
            context=""
        )
        
        # Step 2: Build the calculation chain
        steps = []
        current_context = initial_analysis
        for i in range(8):  # Maximum 8 steps
            step_result = await self.generate(
                instruction=f"""Based on the previous result, perform the next calculation step.
                Show all intermediate results and maintain units. 
                Previous context: {current_context}""",
                context=current_context
            )
            # Validate the step
            validated_step = await self.revise(
                instruction="Check for consistency and correctness in this step.",
                context=step_result
            )
            steps.append(validated_step)
            current_context = validated_step
            
            # Terminate if the final answer is reached
            if "final answer" in validated_step.lower():
                break
        
        # Step 3: Handle multiple approaches (if applicable)
        alternative_solutions = await asyncio.gather(
            self.generate(
                instruction="Solve the problem using an alternative approach.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve the problem using another alternative approach.",
                context=initial_analysis
            )
        )
        best_solution = await self.ensemble(
            instruction="Select the most accurate and efficient solution.",
            contexts_list=[current_context] + alternative_solutions
        )
        
        # Step 4: Summarize and extract the final answer
        summary = await self.summarize(
            instruction="Condense the solution into a clear, concise format. Extract the final numerical answer.",
            context=best_solution
        )
        
        # Return the final answer
        return summary