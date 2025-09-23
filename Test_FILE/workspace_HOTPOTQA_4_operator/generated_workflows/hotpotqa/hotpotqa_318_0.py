# Workflow ID: hotpotqa_318_0
# Benchmark: hotpotqa
# Data Indices: [159]

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

        # Step 1: Initial Analysis and Classification
        initial_analysis = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Bridge Question: Connects documents through shared entities.
            - Comparison Question: Compares properties across documents.
            - Compositional Question: Combines multiple facts to derive an answer.
            
            Additionally, extract all named entities, numbers, and relationships:
            - Entities: People, places, organizations, etc.
            - Numbers: Dates, quantities, etc.
            - Relationships: Actions, connections between entities.
            
            Provide structured classification and extraction results.""",
            context=""
        )

        # Step 2: Entity Linking and Relationship Mapping
        entity_mapping = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {initial_analysis}
            
            Map each entity to the corresponding document title where it appears.
            Identify potential connections between entities across documents.
            Highlight any shared entities that could serve as bridges.
            
            Provide a structured mapping of entities to documents and list potential connections.""",
            context=initial_analysis
        )

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Using the entity mapping and connections:
            {entity_mapping}
            
            Construct a reasoning chain to answer the question:
            - Start with the primary entity related to the question.
            - Follow connections to other entities across documents.
            - Continue until reaching the final entity that provides the answer.
            
            Provide a step-by-step reasoning chain with references to document titles and sentences.""",
            context=entity_mapping
        )

        # Step 4: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer from the final document in the chain.
            Validate the answer against the supporting facts mentioned in the reasoning chain.
            Ensure the answer is factually correct and supported by the documents.
            
            Provide the extracted answer and validation results.""",
            context=reasoning_chain
        )

        # Step 5: Final Answer Refinement
        final_answer = await self.revise(
            instruction="Ensure the answer is clear, concise, and directly addresses the question.",
            context=answer_extraction
        )

        return final_answer