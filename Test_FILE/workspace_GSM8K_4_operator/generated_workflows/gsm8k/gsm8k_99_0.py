# Workflow ID: gsm8k_99_0
# Benchmark: gsm8k
# Data Indices: [89, 258]

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

        # Phase 1: Problem Analysis and Extraction
        problem_analysis = await self.generate(
            instruction="""Extract all key components from the problem:
            - Entities: Identify all named objects, people, or quantities.
            - Relationships: Describe how entities interact (e.g., percentages, comparisons).
            - Constraints: List explicit or implicit conditions.
            Format the output as a structured summary.""",
            context=""
        )

        # Phase 2: Solution Strategy Generation
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a mathematical solution strategy based on:
                {problem_analysis}
                Focus on direct computation and precise arithmetic.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Develop a logical solution strategy based on:
                {problem_analysis}
                Emphasize unit tracking and consistency checks.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Develop a heuristic solution strategy based on:
                {problem_analysis}
                Use estimation and practical reasoning to validate results.""",
                context=problem_analysis
            )
        )
        best_strategy = await self.ensemble(
            instruction="Select the most robust and accurate solution strategy.",
            contexts_list=strategies
        )

        # Phase 3: Sequential Calculation and Validation
        steps = []
        current_context = best_strategy
        for i in range(8):  # Limit to 8 steps for safety
            step_result = await self.generate(
                instruction=f"""Perform the next calculation step based on:
                {current_context}
                Ensure clarity and precision in your reasoning.""",
                context=current_context
            )
            validated_step = await self.revise(
                instruction=f"""Validate the following step:
                {step_result}
                Check for accuracy, consistency, and logical flow.""",
                context=step_result
            )
            steps.append(validated_step)
            current_context = validated_step
            if "final answer" in validated_step.lower():
                break  # Exit loop if final answer is reached

        # Phase 4: Final Answer Synthesis
        final_answer = await self.summarize(
            instruction="Condense the reasoning chain into a single numerical answer.",
            context="\n".join(steps)
        )

        return final_answer