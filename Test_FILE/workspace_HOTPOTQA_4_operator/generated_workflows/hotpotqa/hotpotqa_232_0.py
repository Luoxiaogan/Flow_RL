# Workflow ID: hotpotqa_232_0
# Benchmark: hotpotqa
# Data Indices: [192, 220]

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

        # Phase 1: Problem Understanding
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine its type and key components:
            - Identify if it's a bridge, comparison, or compositional question.
            - Extract key entities and relationships mentioned in the question.
            - Highlight any specific constraints or conditions.
            Provide a structured summary of the question's requirements.""",
            context=""
        )

        # Phase 2: Document Analysis
        # Extract and summarize key information from each document
        document_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document:
                - Extract all named entities, relationships, and key facts.
                - Summarize the document's main points concisely.
                - Highlight any information relevant to the question.
                Document Content: {doc}""",
                context=question_analysis
            ) for doc in re.findall(r"Document \d+:.*?(?=\n\n|$)", self.problem_text, re.DOTALL)]
        )

        # Phase 3: Entity Linking
        # Identify bridge entities connecting documents
        entity_links = await self.ensemble(
            instruction="""Compare entities across documents to find connections:
            - Identify shared entities or related concepts.
            - Prioritize entities mentioned in the question.
            - Build a mapping of entities and their relationships across documents.""",
            contexts_list=document_summaries
        )

        # Phase 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified entity links:
            {entity_links}
            
            Construct a reasoning chain to answer the question:
            - Follow relationships between entities across documents.
            - Validate each step with supporting facts.
            - Ensure the chain logically connects to the question's requirements.""",
            context=entity_links
        )

        # Phase 5: Answer Extraction and Validation
        final_answer = await self.generate(
            instruction=f"""Extract the final answer from the reasoning chain:
            {reasoning_chain}
            
            Validate the answer:
            - Ensure it is factually correct based on the documents.
            - Confirm it directly addresses the question.
            - Provide the exact answer span or yes/no response.""",
            context=reasoning_chain
        )

        return final_answer