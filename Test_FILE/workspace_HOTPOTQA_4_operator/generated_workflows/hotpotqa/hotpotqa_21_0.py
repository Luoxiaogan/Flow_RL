# Workflow ID: hotpotqa_21_0
# Benchmark: hotpotqa
# Data Indices: [307]

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
        
        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type (bridge, comparison, compositional).
            Extract key entities and relationships mentioned in the question and documents.
            Provide structured classification.""",
            context=""
        )
        
        # Step 2: Parallel Entity Extraction
        documents = ["Document 1", "Document 2", "Document 3", "Document 4", "Document 5", 
                     "Document 6", "Document 7", "Document 8", "Document 9", "Document 10"]
        entity_extractions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract entities from {doc} that could serve as bridge entities.
                Focus on named entities, relationships, and key facts.""",
                context=""
            ) for doc in documents]
        )
        
        # Step 3: Synthesize Bridge Entities
        bridge_entities = await self.ensemble(
            instruction="""Compare entities extracted from different documents and identify common entities that can serve as bridges.
            Select the most relevant bridge entities.""",
            contexts_list=entity_extractions
        )
        
        # Step 4: Build Reasoning Chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities: {bridge_entities}
            Construct a reasoning chain that connects the information across documents to answer the question.""",
            context=bridge_entities
        )
        
        # Step 5: Extract Precise Answer
        precise_answer = await self.generate(
            instruction=f"""From the constructed reasoning chain: {reasoning_chain}
            Extract the precise answer span that directly answers the question.""",
            context=reasoning_chain
        )
        
        # Step 6: Validate and Refine
        final_answer = await self.revise(
            instruction=f"""Verify the extracted answer: {precise_answer} against the documents.
            Correct any inaccuracies and ensure the answer is precise and factual.""",
            context=precise_answer
        )
        
        return final_answer