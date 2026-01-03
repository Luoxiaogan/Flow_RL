# Workflow ID: hotpotqa_13_0
# Benchmark: hotpotqa
# Data Indices: [459]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities and their relationships.
            3. Highlight potential bridge entities and their connections across documents.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Reasoning Chain Construction - Build reasoning paths
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Construct a reasoning chain for bridge entities:
                {initial_analysis}
                
                Trace connections between entities across documents.
                Hypothesize intermediate steps and validate their logical consistency.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Construct a reasoning chain for comparison:
                {initial_analysis}
                
                Extract comparable attributes and determine their relationship.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Construct a reasoning chain for composition:
                {initial_analysis}
                
                Combine multiple facts iteratively to derive the final answer.""",
                context=initial_analysis
            )
        )

        # Step 3: Parallel Exploration - Evaluate multiple reasoning paths
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine reasoning chain for accuracy and clarity: {path}",
                context=path
            ) for path in reasoning_paths]
        )

        # Step 4: Answer Extraction and Validation
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer span from the reasoning chain:
                {path}
                
                Ensure the answer is factually correct and aligns with the evidence chain.""",
                context=path
            ) for path in refined_paths]
        )

        # Step 5: Final Synthesis - Select best answer
        final_answer = await self.ensemble(
            instruction="Select the most accurate and well-supported answer.",
            contexts_list=candidate_answers
        )

        # Step 6: Summarize Final Output
        summary = await self.summarize(
            instruction="Provide a concise summary of the final answer and supporting facts.",
            context=final_answer
        )

        return summary