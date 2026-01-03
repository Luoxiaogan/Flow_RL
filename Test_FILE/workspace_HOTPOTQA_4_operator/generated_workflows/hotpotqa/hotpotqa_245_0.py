# Workflow ID: hotpotqa_245_0
# Benchmark: hotpotqa
# Data Indices: [319]

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
        
        # Initial analysis to classify question type and extract key information
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type: bridge, comparison, or compositional.
            2. Extract key entities and relationships from the documents.
            3. Identify potential bridge entities that connect documents.
            Provide structured classification and extracted information.""",
            context=""
        )
        
        # Parallel processing of documents to extract relevant information
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document ")[1:]
        document_tasks = [
            self.generate(
                instruction=f"""Extract entities, relationships, and any direct answers from this document:
                {doc}
                Focus on information relevant to the question type identified earlier.""",
                context=initial_analysis
            ) for doc in documents if doc.strip()
        ]
        document_results = await asyncio.gather(*document_tasks)
        
        # Entity matching and reasoning chain building
        entity_matching = await self.ensemble(
            instruction="""Identify overlapping entities across documents:
            1. Find entities that appear in multiple documents.
            2. Determine how these entities connect to form reasoning chains.
            Provide a clear mapping of entities and their connections.""",
            contexts_list=document_results
        )
        
        reasoning_chain = await self.generate(
            instruction=f"""Based on the identified entities and connections:
            {entity_matching}
            
            Construct a reasoning chain that leads to the answer:
            - Start with the question entity.
            - Follow the connections through bridge entities.
            - End with the final entity that provides the answer.
            Articulate each step in the chain with supporting evidence from the documents.""",
            context=entity_matching
        )
        
        # Answer extraction and validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            {reasoning_chain}
            
            Ensure the answer is a short text span or yes/no response, directly supported by evidence.""",
            context=reasoning_chain
        )
        
        final_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            {answer_extraction}
            
            Ensure it is factually correct and supported by evidence from the documents.
            If necessary, refine the answer for clarity and precision.""",
            context=answer_extraction
        )
        
        return final_answer