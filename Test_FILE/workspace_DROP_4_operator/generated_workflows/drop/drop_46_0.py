# Workflow ID: drop_46_0
# Benchmark: drop
# Data Indices: [327, 354]

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

        # Initial analysis to classify the problem and extract key information
        initial_analysis = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            1. Arithmetic (addition, subtraction, etc.)
            2. Counting (how many times, how many different, etc.)
            3. Comparison (which is greater, which came first, etc.)
            4. Span Extraction (who did, what was the name of, etc.)
            5. Multi-step (requires combining multiple operations)
            
            Extract all relevant entities, numbers, and relationships from the passage. 
            Provide a structured summary of the problem type and extracted information.""",
            context=""
        )

        # Branch based on problem type
        if "arithmetic" in initial_analysis.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation based on the extracted information:
                {initial_analysis}
                
                Show all steps and ensure the final answer is accurate.""",
                context=initial_analysis
            )
        elif "counting" in initial_analysis.lower():
            result = await self.generate(
                instruction=f"""Count the relevant instances based on the extracted information:
                {initial_analysis}
                
                Ensure all instances are considered and counted accurately.""",
                context=initial_analysis
            )
        elif "comparison" in initial_analysis.lower():
            result = await self.generate(
                instruction=f"""Compare the relevant values based on the extracted information:
                {initial_analysis}
                
                Clearly state which value is greater, lesser, or if they are equal.""",
                context=initial_analysis
            )
        elif "span extraction" in initial_analysis.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question based on the extracted information:
                {initial_analysis}
                
                Ensure the span is an exact match from the passage.""",
                context=initial_analysis
            )
        else:  # Multi-step
            steps = await asyncio.gather(
                self.generate(instruction="Perform the first operation...", context=initial_analysis),
                self.generate(instruction="Perform the second operation...", context=initial_analysis)
            )
            result = await self.ensemble(
                instruction="Combine the results of the operations into a coherent answer.",
                contexts_list=steps
            )

        # Refinement to improve the result
        refined_result = await self.revise(
            instruction="Improve clarity, correct any errors, and ensure the answer matches the expected format.",
            context=result
        )

        return refined_result