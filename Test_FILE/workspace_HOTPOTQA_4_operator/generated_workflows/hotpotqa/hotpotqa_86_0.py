# Workflow ID: hotpotqa_86_0
# Benchmark: hotpotqa
# Data Indices: [378]

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

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question type based on the following criteria:
            - Bridge Question: Requires connecting entities across documents.
            - Comparison Question: Involves comparing properties or attributes.
            - Compositional Question: Combines multiple facts to derive the answer.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities_task = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships from the documents.
            Format as structured lists:
            - Entities: [names, roles, and types]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities]""",
            context=question_type
        )

        # Step 3: Construct the evidence chain (parallel processing)
        bridge_entities = await self.generate(
            instruction=f"""Identify bridge entities that connect documents.
            Use the extracted entities: {entities_task}
            Find shared concepts or relationships that link documents logically.""",
            context=entities_task
        )
        evidence_tasks = []
        for i in range(3):  # Process up to 3 potential bridges
            evidence_tasks.append(
                self.generate(
                    instruction=f"""Trace the reasoning chain for bridge entity {i+1}.
                    Connect facts across documents in a logical sequence.""",
                    context=bridge_entities
                )
            )
        evidence_chains = await asyncio.gather(*evidence_tasks)

        # Step 4: Synthesize the answer
        synthesized_answer = await self.ensemble(
            instruction="""Select the most supported answer based on the evidence chains.
            Ensure the answer is a precise span from the documents.""",
            contexts_list=evidence_chains
        )

        # Step 5: Validate and refine the answer
        refined_answer = await self.revise(
            instruction="""Verify the answer against the reasoning chain.
            Ensure it is factually correct and matches the expected format.""",
            context=synthesized_answer
        )

        return refined_answer