# Workflow ID: hotpotqa_27_0
# Benchmark: hotpotqa
# Data Indices: [202]

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

        # Step 1: Initial Analysis - Classify the question and extract key entities
        classification = await self.generate(
            instruction="""Analyze the question to determine its type:
            - Is it a bridge question requiring shared entities?
            - Is it a comparison question involving properties?
            - Is it a compositional question combining multiple facts?
            Also, extract key entities and relationships mentioned in the question.""",
            context=""
        )

        # Step 2: Parallel Document Processing - Extract relevant facts from each document
        documents = re.findall(r"Document \d+:.*?(?=\n\n|$)", self.problem_text, re.DOTALL)
        document_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all relevant facts, entities, and relationships from this document:
                {doc}""",
                context=""
            ) for doc in documents]
        )

        # Step 3: Reasoning Chain Construction - Build connections based on question type
        reasoning_chain = await self.ensemble(
            instruction=f"""Based on the question type ({classification}), construct a reasoning chain:
            - For bridge questions, identify shared entities and connect documents.
            - For comparison questions, extract comparable properties and determine the relationship.
            - For compositional questions, combine multiple facts to derive the answer.
            Use the following extracted facts from each document:
            {document_facts}""",
            contexts_list=document_facts
        )

        # Step 4: Validation and Refinement - Ensure accuracy and refine if necessary
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain for consistency and factual accuracy:
            {reasoning_chain}
            Identify any issues or missing information.""",
            context=""
        )
        if "issue" in validation.lower() or "missing" in validation.lower():
            refined_chain = await self.revise(
                instruction=f"""Refine the reasoning chain to address the following issues:
                {validation}""",
                context=reasoning_chain
            )
            reasoning_chain = refined_chain

        # Step 5: Answer Extraction - Extract the precise answer span
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the reasoning chain:
            {reasoning_chain}
            Ensure the answer is supported by explicit evidence from the documents.""",
            context=""
        )

        return answer.strip()