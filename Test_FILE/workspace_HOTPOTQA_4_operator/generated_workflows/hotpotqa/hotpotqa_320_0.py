# Workflow ID: hotpotqa_320_0
# Benchmark: hotpotqa
# Data Indices: [381, 289]

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

        # Step 1: Initial Analysis - Identify question type, entities, and relationships
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Identify potential bridge entities if applicable.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple reasoning paths
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Explore reasoning paths based on bridge entities.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Explore reasoning paths based on comparisons.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis:
                {initial_analysis}
                
                Explore reasoning paths based on composition.""",
                context=initial_analysis
            )
        )

        # Step 3: Validate and Refine Reasoning Paths
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine this reasoning path for accuracy and completeness.",
                context=path
            ) for path in reasoning_paths]
        )

        # Step 4: Synthesize Results - Select the best reasoning chain
        synthesis = await self.ensemble(
            instruction="Evaluate reasoning paths and select the most plausible one.",
            contexts_list=refined_paths
        )

        # Step 5: Extract and Verify Final Answer
        final_answer = await self.generate(
            instruction=f"""Using the selected reasoning chain:
            {synthesis}
            
            Extract the precise answer from the documents.
            Ensure the answer is factually correct and supported by evidence.""",
            context=synthesis
        )

        # Step 6: Summarize Supporting Facts
        supporting_facts = await self.summarize(
            instruction="Condense the supporting facts into a concise summary.",
            context=final_answer
        )

        return {
            "answer": final_answer,
            "supporting_facts": supporting_facts
        }