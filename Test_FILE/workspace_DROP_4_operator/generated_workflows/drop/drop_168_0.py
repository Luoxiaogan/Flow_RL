# Workflow ID: drop_168_0
# Benchmark: drop
# Data Indices: [253, 157]

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

        # Step 1: Initial Analysis - Extract entities, classify question type, resolve references
        initial_analysis = await self.generate(
            instruction="""Perform an initial analysis of the problem:
            1. Extract all named entities, numbers, and their relationships from the passage.
            2. Classify the question type (arithmetic, counting, comparison, span extraction).
            3. Resolve any pronouns or partial references in the question to specific entities in the passage.
            Provide a structured breakdown with clear categories.""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore multiple solution paths
        arithmetic_path = self.generate(
            instruction=f"""If the question involves arithmetic:
            - Extract all relevant numerical data from the passage.
            - Identify the required operation (addition, subtraction, etc.).
            - Perform the calculation and provide the result.
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        comparison_path = self.generate(
            instruction=f"""If the question involves comparison:
            - Extract comparable attributes (e.g., dates, quantities) from the passage.
            - Determine the basis of comparison (greater, earlier, etc.).
            - Compare the attributes and provide the result.
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        span_extraction_path = self.generate(
            instruction=f"""If the question involves span extraction:
            - Identify the exact phrase in the passage that answers the question.
            - Ensure the span matches the passage exactly.
            Context: {initial_analysis}""",
            context=initial_analysis
        )

        # Run paths in parallel
        paths = await asyncio.gather(arithmetic_path, comparison_path, span_extraction_path)

        # Step 3: Validation and Refinement - Validate intermediate results
        validated_paths = []
        for path in paths:
            validation = await self.generate(
                instruction=f"""Validate this solution:
                - Check consistency with the passage.
                - Identify any errors or missing information.
                Context: {path}""",
                context=path
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine this solution based on validation feedback:
                    Feedback: {validation}
                    Original Solution: {path}""",
                    context=path
                )
                validated_paths.append(refined)
            else:
                validated_paths.append(path)

        # Step 4: Final Synthesis - Select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Select or synthesize the best solution:
            - Evaluate accuracy, completeness, and alignment with the question.
            - Choose the most robust and well-supported answer.""",
            contexts_list=validated_paths
        )

        return final_solution