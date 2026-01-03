# Workflow ID: gsm8k_79_0
# Benchmark: gsm8k
# Data Indices: [17, 215]

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

        # Initial analysis to extract key information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, named entities, and relationships.
            Classify the problem type:
            - Sequential Operations
            - Rate Problems
            - Distribution
            - Proportions
            - Multi-entity
            Provide structured classification.""",
            context=""
        )

        # Conditional branching based on problem type
        if "sequential" in initial_analysis.lower():
            # Sequential Operations Path
            steps = await self.generate(
                instruction=f"""Based on the initial analysis: {initial_analysis}
                Generate step-by-step calculations showing intermediate results.
                Ensure each step logically follows from the previous one.""",
                context=initial_analysis
            )
            refined_steps = await self.revise(
                instruction="Verify each step's correctness and improve clarity.",
                context=steps
            )
            final_answer = await self.generate(
                instruction="Extract the final numerical answer from the refined steps.",
                context=refined_steps
            )
        elif "rate" in initial_analysis.lower():
            # Rate Problems Path
            rate_analysis = await self.generate(
                instruction=f"""Analyze the rate problem: {initial_analysis}
                Identify rates, times, and distances involved.
                Generate necessary calculations.""",
                context=initial_analysis
            )
            validated_rate = await self.revise(
                instruction="Validate rate calculations and ensure units are consistent.",
                context=rate_analysis
            )
            final_answer = await self.generate(
                instruction="Extract the final numerical answer from the validated rate analysis.",
                context=validated_rate
            )
        elif "distribution" in initial_analysis.lower():
            # Distribution Path
            distribution_steps = await self.generate(
                instruction=f"""Analyze the distribution problem: {initial_analysis}
                Generate steps for dividing quantities and handling remainders.""",
                context=initial_analysis
            )
            refined_distribution = await self.revise(
                instruction="Ensure distribution steps are clear and accurate.",
                context=distribution_steps
            )
            final_answer = await self.generate(
                instruction="Extract the final numerical answer from the refined distribution steps.",
                context=refined_distribution
            )
        elif "proportions" in initial_analysis.lower():
            # Proportions Path
            proportion_steps = await self.generate(
                instruction=f"""Analyze the proportion problem: {initial_analysis}
                Generate steps for handling percentages, fractions, and ratios.""",
                context=initial_analysis
            )
            refined_proportions = await self.revise(
                instruction="Verify proportion calculations and improve clarity.",
                context=proportion_steps
            )
            final_answer = await self.generate(
                instruction="Extract the final numerical answer from the refined proportion steps.",
                context=refined_proportions
            )
        else:
            # Default Comprehensive Approach
            comprehensive_solution = await self.generate(
                instruction=f"""Using the initial analysis: {initial_analysis}
                Develop a comprehensive solution showing all necessary calculations.""",
                context=initial_analysis
            )
            refined_solution = await self.revise(
                instruction="Critique and refine the comprehensive solution.",
                context=comprehensive_solution
            )
            final_answer = await self.generate(
                instruction="Extract the final numerical answer from the refined comprehensive solution.",
                context=refined_solution
            )

        # Ensemble to ensure the best possible final answer
        ensemble_result = await self.ensemble(
            instruction="Synthesize all paths to determine the most accurate final answer.",
            contexts_list=[final_answer]
        )

        return ensemble_result