# Workflow ID: drop_185_0
# Benchmark: drop
# Data Indices: [113, 313]

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

        # Step 1: Initial Analysis - Extract entities and classify the problem
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Classify the problem type as one of the following:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/longer, which came first, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            - Multi-step (requires chaining multiple operations or facts)
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Parallel Processing - Handle different problem types
        problem_type = await self.generate(
            instruction="Identify the primary problem type from the analysis.",
            context=initial_analysis
        )

        if "arithmetic" in problem_type.lower():
            # Perform arithmetic operations
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation based on the question.
                Use the extracted numbers and relationships from: {initial_analysis}""",
                context=initial_analysis
            )
            refined_result = await self.revise(
                instruction="Ensure calculations are accurate and formatted correctly.",
                context=arithmetic_result
            )
            final_answer = refined_result

        elif "counting" in problem_type.lower():
            # Count occurrences of specific entities or actions
            count_tasks = await asyncio.gather(
                self.generate(
                    instruction=f"Count occurrences of each relevant entity/action from: {initial_analysis}",
                    context=initial_analysis
                ),
                self.generate(
                    instruction=f"Verify counts by cross-referencing with the passage: {initial_analysis}",
                    context=initial_analysis
                )
            )
            synthesized_count = await self.ensemble(
                instruction="Combine counts and resolve discrepancies.",
                contexts_list=count_tasks
            )
            final_answer = synthesized_count

        elif "comparison" in problem_type.lower():
            # Compare entities or values
            comparison_result = await self.generate(
                instruction=f"""Compare the relevant entities/values based on the question.
                Use the extracted data from: {initial_analysis}""",
                context=initial_analysis
            )
            refined_comparison = await self.revise(
                instruction="Ensure the comparison is logically sound and clearly stated.",
                context=comparison_result
            )
            final_answer = refined_comparison

        elif "span extraction" in problem_type.lower():
            # Extract exact text spans
            span_extraction = await self.generate(
                instruction=f"""Extract the exact text span that answers the question.
                Use the passage and analysis: {initial_analysis}""",
                context=initial_analysis
            )
            refined_span = await self.revise(
                instruction="Ensure the extracted span matches the passage exactly.",
                context=span_extraction
            )
            final_answer = refined_span

        else:
            # Handle multi-step reasoning
            steps = await self.generate(
                instruction=f"""Break the problem into sub-steps and solve each step sequentially.
                Use the analysis: {initial_analysis}""",
                context=initial_analysis
            )
            refined_steps = await self.revise(
                instruction="Refine each step to ensure logical consistency and accuracy.",
                context=steps
            )
            final_answer = refined_steps

        # Step 3: Final Validation and Formatting
        validated_answer = await self.revise(
            instruction="Validate the final answer against the question and format it appropriately.",
            context=final_answer
        )

        return validated_answer