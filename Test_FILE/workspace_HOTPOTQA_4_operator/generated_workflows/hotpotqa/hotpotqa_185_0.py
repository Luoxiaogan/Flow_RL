# Workflow ID: hotpotqa_185_0
# Benchmark: hotpotqa
# Data Indices: [436, 371]

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
            instruction="""Analyze the question and context documents:
            - Identify all named entities (people, places, organizations, dates, etc.)
            - Extract relationships between entities
            - Classify the question type (bridge, comparison, compositional)
            - Provide structured output with clear labels for each component""",
            context=""
        )

        # Step 2: Parallel Exploration
        bridge_path = self.generate(
            instruction=f"""Follow bridge entities to connect documents:
            - Use entities from: {initial_analysis}
            - Find explicit connections between documents
            - Trace reasoning chains step-by-step""",
            context=initial_analysis
        )
        comparison_path = self.generate(
            instruction=f"""Compare properties across documents:
            - Use entities from: {initial_analysis}
            - Identify comparable attributes (e.g., dates, rankings)
            - Perform necessary calculations or evaluations""",
            context=initial_analysis
        )
        compositional_path = self.generate(
            instruction=f"""Combine multiple facts sequentially:
            - Use entities from: {initial_analysis}
            - Chain facts logically to derive the answer
            - Ensure each step is supported by evidence""",
            context=initial_analysis
        )

        # Execute parallel paths
        paths_results = await asyncio.gather(bridge_path, comparison_path, compositional_path)

        # Step 3: Conditional Branching
        question_type = await self.generate(
            instruction=f"""Determine the most likely question type based on:
            {initial_analysis}
            And select the corresponding path result.""",
            context=initial_analysis
        )

        if "bridge" in question_type.lower():
            selected_path = paths_results[0]
        elif "comparison" in question_type.lower():
            selected_path = paths_results[1]
        else:
            selected_path = paths_results[2]

        # Step 4: Iterative Refinement
        refined_result = selected_path
        for _ in range(2):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                - Check for logical consistency
                - Verify factual accuracy
                - Identify gaps or ambiguities""",
                context=refined_result
            )
            if "error" in validation.lower() or "gap" in validation.lower():
                refined_result = await self.revise(
                    instruction=f"""Refine the reasoning chain:
                    - Address issues identified in validation: {validation}
                    - Improve clarity and precision""",
                    context=refined_result
                )
            else:
                break

        # Step 5: Final Synthesis
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the final answer:
            - Use reasoning chain: {refined_result}
            - Extract precise answer span from the text
            - Include supporting facts from different documents""",
            contexts_list=paths_results
        )

        return final_answer