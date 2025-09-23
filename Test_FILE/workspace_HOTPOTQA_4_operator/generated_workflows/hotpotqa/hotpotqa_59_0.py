# Workflow ID: hotpotqa_59_0
# Benchmark: hotpotqa
# Data Indices: [295, 304]

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
        import re
        
        # Initial analysis to classify question type and extract key components
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional).
            Extract key entities and relationships mentioned in the question.
            Identify relevant documents based on the question context.""",
            context=""
        )
        
        # Extract entities and relationships from each document in parallel
        documents = re.findall(r'Document \d+: (.+?)\n', self.problem_text)
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities and relationships from this document:
                Document: {doc}
                Focus on entities and relationships relevant to the question.""",
                context=initial_analysis
            ) for doc in documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)
        
        # Build reasoning chains by connecting extracted entities
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Connect extracted entities to form reasoning chains:
                Extracted Entities: {entities}
                Ensure chains are logically consistent and factually supported.""",
                context=initial_analysis
            ) for entities in extracted_entities]
        )
        
        # Validate and refine reasoning chains
        validated_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate this reasoning chain:
                Reasoning Chain: {chain}
                Ensure factual accuracy and logical consistency.""",
                context=chain
            ) for chain in reasoning_chains]
        )
        
        # Summarize each validated reasoning chain into concise answers
        summarized_answers = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Summarize this reasoning chain into a short, precise answer:
                Reasoning Chain: {chain}""",
                context=chain
            ) for chain in validated_chains]
        )
        
        # Ensemble to select the most accurate and supported answer
        final_answer = await self.ensemble(
            instruction="""Select the most accurate and factually supported answer:
            Consider all reasoning chains and choose the best-supported option.""",
            contexts_list=summarized_answers
        )
        
        return final_answer