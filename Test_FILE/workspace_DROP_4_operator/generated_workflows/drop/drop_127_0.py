# Workflow ID: drop_127_0
# Benchmark: drop
# Data Indices: [46, 71]

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
            instruction="""Analyze the passage and question:
            - Extract all named entities, numbers, and relationships.
            - Classify the question type (arithmetic, counting, comparison, span extraction).
            - Highlight potential ambiguities or missing information.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        arithmetic_path, counting_path, comparison_path, span_extraction_path = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem assuming it requires arithmetic:
                - Identify relevant numbers and their relationships.
                - Perform necessary calculations (addition, subtraction, etc.).
                - Present the result in the expected format.
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it requires counting:
                - Identify relevant entities and count their occurrences.
                - Present the result in the expected format.
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it requires comparison:
                - Identify entities or values to compare.
                - Evaluate relative magnitudes or orders.
                - Present the result in the expected format.
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it requires span extraction:
                - Identify exact text spans matching the query.
                - Present the result in the expected format.
                Context: {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Synthesis
        validated_results = await asyncio.gather(
            self.revise(
                instruction="Validate the arithmetic solution for correctness and clarity.",
                context=arithmetic_path
            ),
            self.revise(
                instruction="Validate the counting solution for correctness and clarity.",
                context=counting_path
            ),
            self.revise(
                instruction="Validate the comparison solution for correctness and clarity.",
                context=comparison_path
            ),
            self.revise(
                instruction="Validate the span extraction solution for correctness and clarity.",
                context=span_extraction_path
            )
        )

        final_answer = await self.ensemble(
            instruction="Synthesize the validated results into a single coherent answer.",
            contexts_list=validated_results
        )

        # Step 4: Feedback Loop for Refinement
        MAX_ITERATIONS = 3
        for _ in range(MAX_ITERATIONS):
            validation_summary = await self.generate(
                instruction="Identify unresolved issues or ambiguities in the current solution.",
                context=final_answer
            )
            if "issue" not in validation_summary.lower() and "ambiguity" not in validation_summary.lower():
                break
            refined_answer = await self.revise(
                instruction=f"Refine the solution based on identified issues: {validation_summary}",
                context=final_answer
            )
            final_answer = refined_answer

        return final_answer