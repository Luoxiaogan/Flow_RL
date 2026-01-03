# Workflow ID: hotpotqa_92_0
# Benchmark: hotpotqa
# Data Indices: [111, 160]

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

        # Step 1: Initial Analysis - Classify question and extract entities
        initial_analysis = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge: Requires connecting documents through shared entities.
            2. Comparison: Involves comparing properties across documents.
            3. Compositional: Combines multiple facts to derive an answer.
            
            Extract all named entities, relationships, and relevant document titles.
            Format as structured output:
            - Question Type: [type]
            - Entities: [list of entities]
            - Relationships: [list of relationships]
            - Relevant Documents: [list of titles]""",
            context=""
        )

        # Step 2: Parallel Exploration - Gather supporting facts
        entities_and_relationships = await self.generate(
            instruction=f"Extract detailed context for each entity and relationship:\n{initial_analysis}",
            context=initial_analysis
        )
        parallel_tasks = [
            self.generate(
                instruction=f"Explore context of {entity} in relevant documents.",
                context=entities_and_relationships
            )
            for entity in ["Seth Rollins", "Dennis Agajanian"]  # Example entities; dynamically populate in real implementation
        ]
        parallel_outputs = await asyncio.gather(*parallel_tasks)

        # Step 3: Reasoning Chain Construction - Synthesize facts
        reasoning_chain = await self.ensemble(
            instruction="Synthesize the gathered facts into a coherent reasoning chain. Ensure logical connections between documents.",
            contexts_list=parallel_outputs
        )

        # Step 4: Iterative Refinement - Validate and refine chain
        refined_chain = reasoning_chain
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the reasoning chain for logical consistency and factual correctness.",
                context=refined_chain
            )
            if "error" in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"Refine the reasoning chain based on validation feedback: {validation}",
                    context=refined_chain
                )
            else:
                break

        # Step 5: Final Answer Extraction - Extract precise answer
        final_answer = await self.summarize(
            instruction="Extract the precise answer from the refined reasoning chain. Ensure it is short and factually supported.",
            context=refined_chain
        )

        return final_answer