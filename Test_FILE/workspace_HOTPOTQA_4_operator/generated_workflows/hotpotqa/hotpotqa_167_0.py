# Workflow ID: hotpotqa_167_0
# Benchmark: hotpotqa
# Data Indices: [18]

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
        
        # Step 1: Classify question type and extract key entities/relationships
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting entities across documents
            - Comparison: Requires comparing properties across documents
            - Compositional: Requires combining multiple facts
            
            Then, extract all key entities and relationships from the question and context documents.
            Format the output as:
            Question Type: [type]
            Entities: [list of entities]
            Relationships: [list of relationships]""",
            context=""
        )
        
        # Step 2: Map entities to documents
        entities = [line.split(":")[1].strip() for line in classification.split("\n") if "Entities" in line][0]
        entity_mapping = await self.generate(
            instruction=f"""For each entity in the list: {entities},
            identify the document(s) where the entity is mentioned.
            Provide the mapping as:
            Entity: [entity]
            Document: [document title]""",
            context=classification
        )
        
        # Step 3: Build reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using the entity-document mapping: {entity_mapping},
                construct a reasoning chain starting from the first entity.
                Follow connections across documents to reach the final answer.
                Provide the chain as:
                Step 1: [fact from document X]
                Step 2: [fact from document Y]
                Final Answer: [answer]""",
                context=entity_mapping
            ) for _ in range(3)]  # Explore up to 3 chains
        )
        
        # Step 4: Validate reasoning chains
        validated_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the reasoning chain: {chain}.
                Ensure each step is factually supported by the documents.
                If discrepancies are found, suggest corrections.""",
                context=chain
            ) for chain in reasoning_chains]
        )
        
        # Step 5: Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Compare the reasoning chains and select the most plausible one.
            Criteria:
            - Coherence: Does the chain make logical sense?
            - Factual Support: Is each step supported by the documents?
            - Alignment: Does the chain answer the question correctly?""",
            contexts_list=validated_chains
        )
        
        # Step 6: Extract and summarize the final answer
        final_answer = await self.summarize(
            instruction=f"""From the selected reasoning chain: {best_chain},
            extract the final answer as a short text span directly from the documents.
            Ensure the answer is precise and factually correct.""",
            context=best_chain
        )
        
        return final_answer