# Workflow ID: hotpotqa_3_0
# Benchmark: hotpotqa
# Data Indices: [284]

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
            instruction="""Classify the question type:
            - Is it a bridge question (connecting entities across documents)?
            - A comparison question (evaluating properties across documents)?
            - Or a compositional question (combining multiple facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )
        
        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, relationships, and constraints from the documents:
            - Entities: Names, places, dates, etc.
            - Relationships: How entities are connected
            - Constraints: Any conditions or limitations mentioned""",
            context=""
        )
        summarized_entities = await self.summarize(
            instruction="Condense the extracted entities and relationships into key points.",
            context=entities
        )
        
        # Step 3: Identify document connections via bridge entities
        document_connections = await asyncio.gather(
            *[self.generate(
                instruction=f"""Identify connections between Document {i} and other documents:
                - Shared entities
                - Overlapping relationships
                - Potential reasoning chains""",
                context=summarized_entities
            ) for i in range(1, 11)]  # Assuming 10 documents as per example
        )
        summarized_connections = await self.summarize(
            instruction="Summarize the document connections focusing on bridge entities.",
            context="\n".join(document_connections)
        )
        
        # Step 4: Build reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain using the connection: {connection}
                - Follow logical sequence of facts
                - Ensure chain leads to answer""",
                context=summarized_entities
            ) for connection in summarized_connections.split("\n") if connection.strip()]
        )
        validated_chains = await asyncio.gather(
            *[self.revise(
                instruction="Validate and improve the reasoning chain for accuracy and completeness.",
                context=chain
            ) for chain in reasoning_chains]
        )
        
        # Step 5: Extract and verify the answer
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer from the reasoning chain: {chain}
                - Ensure answer is factual and supported by evidence""",
                context=summarized_entities
            ) for chain in validated_chains]
        )
        final_answer = await self.ensemble(
            instruction="Select the best answer based on factual correctness and supporting evidence.",
            contexts_list=candidate_answers
        )
        
        return final_answer