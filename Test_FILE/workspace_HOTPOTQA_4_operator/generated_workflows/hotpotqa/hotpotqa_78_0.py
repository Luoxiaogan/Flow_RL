# Workflow ID: hotpotqa_78_0
# Benchmark: hotpotqa
# Data Indices: [335]

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

        # Step 1: Classify the question type and extract key entities
        classification = await self.generate(
            instruction="""Analyze the question to determine its type:
            - Is it a bridge question (connecting entities)?
            - Is it a comparison question (contrasting properties)?
            - Is it a compositional question (combining facts)?
            Also, extract key entities mentioned in the question.
            Provide structured output with the question type and entities.""",
            context=""
        )

        # Step 2: Analyze all documents in parallel to extract relevant entities and facts
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        document_analysis_tasks = [
            self.generate(
                instruction=f"""Extract all entities and relevant facts from this document:
                Focus on entities related to the question ({classification}).
                Include relationships and key details.""",
                context=doc
            ) for doc in documents if doc.strip()
        ]
        document_analyses = await asyncio.gather(*document_analysis_tasks)

        # Step 3: Identify bridge entities and construct reasoning chains
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted information from all documents:
            {document_analyses}
            
            Identify bridge entities that connect the documents.
            Construct a reasoning chain that links these entities to answer the question.
            Highlight supporting facts from different documents.""",
            context=classification
        )

        # Step 4: Extract the precise answer span or yes/no response
        answer_extraction = await self.generate(
            instruction=f"""Based on the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the text or provide a yes/no response.
            Ensure the answer is factually correct and directly addresses the question.""",
            context=""
        )

        # Step 5: Validate the answer against the evidence chain
        validation = await self.revise(
            instruction=f"""Verify the correctness of the answer:
            {answer_extraction}
            
            Ensure it is supported by the reasoning chain and evidence from the documents.
            Flag any ambiguities or missing information.""",
            context=reasoning_chain
        )

        # Final Output: Return the validated answer
        return validation