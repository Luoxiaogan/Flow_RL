# Workflow ID: hotpotqa_270_0
# Benchmark: hotpotqa
# Data Indices: [158]

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

        # Initial Analysis: Classify question type and extract key entities
        analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            1. Is this a bridge, comparison, or compositional question?
            2. Identify all entities, relationships, and relevant facts.
            3. Highlight potential bridge entities or shared concepts.
            Provide structured output.""",
            context=""
        )

        # Conditional Branching: Explore reasoning paths based on question type
        if "bridge" in analysis.lower():
            # Bridge Question: Find connections between entities
            paths = await asyncio.gather(
                self.generate(
                    instruction="Find connections between entities across documents.",
                    context=analysis
                ),
                self.generate(
                    instruction="Identify bridge entities and their roles.",
                    context=analysis
                )
            )
        elif "comparison" in analysis.lower():
            # Comparison Question: Extract and compare properties
            paths = await asyncio.gather(
                self.generate(
                    instruction="Extract relevant properties for comparison.",
                    context=analysis
                ),
                self.generate(
                    instruction="Compare properties and determine the answer.",
                    context=analysis
                )
            )
        else:
            # Compositional Question: Combine facts from multiple documents
            paths = await asyncio.gather(
                self.generate(
                    instruction="Combine facts from multiple documents.",
                    context=analysis
                ),
                self.generate(
                    instruction="Derive the final answer from combined facts.",
                    context=analysis
                )
            )

        # Synthesis: Merge insights from parallel paths
        synthesis = await self.ensemble(
            instruction="Merge insights into a coherent reasoning chain.",
            contexts_list=paths
        )

        # Validation: Check if the synthesized result is valid
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain:
            1. Does it answer the question?
            2. Is it supported by evidence from the documents?
            3. Are there any gaps or inconsistencies?
            Provide detailed feedback.""",
            context=synthesis
        )

        # Iterative Refinement: Improve the reasoning chain if needed
        max_iterations = 3
        for _ in range(max_iterations):
            if "error" in validation.lower() or "gap" in validation.lower():
                refined = await self.revise(
                    instruction=f"Refine the reasoning chain based on feedback: {validation}",
                    context=synthesis
                )
                synthesis = refined
                validation = await self.generate(
                    instruction="Re-validate the refined reasoning chain.",
                    context=synthesis
                )
            else:
                break

        # Final Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the final answer from the validated reasoning chain:
            1. Ensure it is a short factual span.
            2. Verify it matches the expected answer format.
            3. Include supporting facts.""",
            context=synthesis
        )

        return answer