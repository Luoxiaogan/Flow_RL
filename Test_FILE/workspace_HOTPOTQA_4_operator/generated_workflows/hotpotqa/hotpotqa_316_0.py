# Workflow ID: hotpotqa_316_0
# Benchmark: hotpotqa
# Data Indices: [93]

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

        # Step 1: Analyze the problem and classify the question type
        problem_analysis = await self.generate(
            instruction="""Analyze the problem and classify it:
            - Identify the question type (bridge, comparison, compositional).
            - Extract key entities, relationships, and constraints from the question.
            - Provide a structured classification.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        document_entities = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all named entities, relationships, and key facts from Document {i+1}.
                Format as a structured list with categories:
                - Entities: [names, roles, types]
                - Relationships: [connections between entities]
                - Key Facts: [important sentences or phrases]""",
                context=""
            ) for i in range(10)]  # Assuming up to 10 documents
        )

        # Step 3: Identify bridge entities (for bridge questions)
        bridge_entity = await self.ensemble(
            instruction="""Identify the most likely bridge entity connecting multiple documents.
            - Compare entities across documents.
            - Select the entity that best connects the reasoning chain.
            - If no clear bridge exists, flag ambiguity.""",
            contexts_list=document_entities
        )

        # Step 4: Construct the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entity: {bridge_entity}
            Construct a reasoning chain that connects facts across documents:
            - Trace relationships between entities.
            - Validate the chain against the question requirements.
            - Ensure logical consistency.""",
            context=problem_analysis
        )

        # Step 5: Refine the reasoning chain
        refined_chain = await self.revise(
            instruction="""Refine the reasoning chain:
            - Address any gaps or inconsistencies.
            - Add missing details or clarify ambiguous connections.
            - Ensure the chain fully supports the answer.""",
            context=reasoning_chain
        )

        # Step 6: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain: {refined_chain}
            - Locate the exact text span in the documents that supports the answer.
            - Validate the answer against the question and supporting facts.
            - Format the answer as a short text span or yes/no response.""",
            context=""
        )

        return answer