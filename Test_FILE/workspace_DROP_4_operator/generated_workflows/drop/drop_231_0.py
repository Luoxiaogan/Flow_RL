# Workflow ID: drop_231_0
# Benchmark: drop
# Data Indices: [122, 420]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Classify the question type (arithmetic, counting, comparison, span extraction, etc.). 
            Resolve references in the question to specific entities in the passage. 
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        arithmetic_solution = self.generate(
            instruction=f"""If the question requires arithmetic, extract relevant numbers and perform the operation. 
            Passage and analysis: {initial_analysis}""",
            context=initial_analysis
        )

        counting_solution = self.generate(
            instruction=f"""If the question requires counting, count occurrences of specific entities or events. 
            Passage and analysis: {initial_analysis}""",
            context=initial_analysis
        )

        comparison_solution = self.generate(
            instruction=f"""If the question requires comparison, compare numerical values or qualitative attributes. 
            Passage and analysis: {initial_analysis}""",
            context=initial_analysis
        )

        span_extraction_solution = self.generate(
            instruction=f"""If the question requires span extraction, extract exact text spans matching the question. 
            Passage and analysis: {initial_analysis}""",
            context=initial_analysis
        )

        # Execute parallel paths
        candidates = await asyncio.gather(
            arithmetic_solution,
            counting_solution,
            comparison_solution,
            span_extraction_solution
        )

        # Step 3: Validation and Refinement
        refined_candidates = await asyncio.gather(
            *[self.revise(instruction="Validate and refine this solution.", context=candidate) 
              for candidate in candidates]
        )

        # Step 4: Ensemble Decision
        final_answer = await self.ensemble(
            instruction="Select the best answer from the refined candidates.",
            contexts_list=refined_candidates
        )

        return final_answer