# Workflow ID: gsm8k_48_0
# Benchmark: gsm8k
# Data Indices: [41, 251]

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

        # Step 1: Initial Analysis - Extract key information and classify problem type
        analysis = await self.generate(
            instruction="""Extract all numerical values, relationships, and constraints. 
            Classify the problem type (e.g., sequential, rate, distribution, proportions, multi-entity). 
            Identify what the question asks for and propose an initial solution path.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution paths
        paths = await asyncio.gather(
            self.generate(
                instruction="Solve using a sequential calculation approach.",
                context=analysis
            ),
            self.generate(
                instruction="Solve using proportional reasoning and scaling.",
                context=analysis
            ),
            self.generate(
                instruction="Solve by breaking the problem into smaller sub-problems.",
                context=analysis
            )
        )

        # Step 3: Validation and Refinement - Check calculations and clarify steps
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction="Validate calculations and clarify ambiguous steps. Ensure units and relationships are consistent.",
                context=path
            ) for path in paths]
        )

        # Step 4: Summarization - Compress reasoning chains into concise summaries
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Extract key findings and compress the reasoning chain into a clear, concise format.",
                context=path
            ) for path in refined_paths]
        )

        # Step 5: Ensemble - Synthesize multiple solution paths into a unified answer
        final_answer = await self.ensemble(
            instruction="Compare solution paths. Select the most accurate and complete solution. Resolve conflicts if necessary.",
            contexts_list=summaries
        )

        # Step 6: Final Validation - Ensure the answer meets requirements
        validated_answer = await self.revise(
            instruction="Double-check the final answer for numerical accuracy and consistency with the problem statement.",
            context=final_answer
        )

        return validated_answer