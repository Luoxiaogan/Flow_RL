# Workflow ID: gsm8k_19_0
# Benchmark: gsm8k
# Data Indices: [21, 262]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Numbers and their context
            - Relationships between quantities
            - Units of measurement
            - What the question is asking for
            Format as a structured list.""",
            context=""
        )
        refined_analysis = await self.revise(
            instruction="Refine the extracted information to ensure completeness and accuracy.",
            context=analysis
        )

        # Phase 2: Solution Construction
        solution_plans = await asyncio.gather(
            self.generate(
                instruction=f"""Create a step-by-step calculation plan based on:
                {refined_analysis}
                Focus on logical connections between quantities.""",
                context=""
            ),
            self.generate(
                instruction=f"""Explore an alternative interpretation of:
                {refined_analysis}
                Consider different ways to interpret ambiguous relationships.""",
                context=""
            )
        )
        best_plan = await self.ensemble(
            instruction="Select the most coherent and complete solution plan.",
            contexts_list=solution_plans
        )

        # Phase 3: Execution and Validation
        execution_steps = await self.generate(
            instruction=f"""Execute the following plan step-by-step:
            {best_plan}
            Show intermediate results and validate each step.""",
            context=""
        )
        validated_steps = await self.revise(
            instruction="Check each step for logical consistency and numerical correctness.",
            context=execution_steps
        )
        condensed_reasoning = await self.summarize(
            instruction="Condense the reasoning chain into a concise format while preserving intermediate results.",
            context=validated_steps
        )

        # Phase 4: Final Output
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from:
            {condensed_reasoning}
            Ensure it is precise and matches the required format.""",
            context=""
        )

        return final_answer.strip()