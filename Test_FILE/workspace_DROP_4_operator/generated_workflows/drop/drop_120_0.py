# Workflow ID: drop_120_0
# Benchmark: drop
# Data Indices: [324, 54]

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
        initial_analysis = await self.generate(
            instruction="""Classify the problem type and extract key information:
            - Is it numerical, logical, or textual?
            - What entities, numbers, and relationships are mentioned in the passage?
            - What is the expected answer format?
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Processing
        numerical_computation = self.generate(
            instruction="""Extract all numbers and perform required arithmetic operations:
            - Identify relevant numbers from the passage
            - Perform addition, subtraction, or other operations as needed
            - Present the result with appropriate units""",
            context=initial_analysis
        )

        textual_extraction = self.generate(
            instruction="""Identify the exact text span that answers the question:
            - Match the question to specific sentences in the passage
            - Extract the verbatim text span
            - Ensure the span matches the expected format""",
            context=initial_analysis
        )

        comparison_counting = self.generate(
            instruction="""Perform comparison or counting operations:
            - Identify relevant entities and their attributes
            - Count occurrences or compare values as needed
            - Present the result clearly""",
            context=initial_analysis
        )

        parallel_results = await asyncio.gather(numerical_computation, textual_extraction, comparison_counting)

        # Step 3: Synthesis
        synthesized_answer = await self.ensemble(
            instruction="""Synthesize results from all branches:
            - Combine numerical, textual, and comparative insights
            - Ensure coherence and alignment with the question
            - Select the best answer based on problem type""",
            contexts_list=parallel_results
        )

        # Step 4: Validation and Refinement
        final_answer = await self.revise(
            instruction="""Validate and refine the answer:
            - Check for errors or inconsistencies
            - Ensure the format matches the expected output
            - Improve clarity and precision""",
            context=synthesized_answer
        )

        return final_answer