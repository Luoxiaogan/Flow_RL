# Workflow ID: hotpotqa_248_0
# Benchmark: hotpotqa
# Data Indices: [293, 182]

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
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting documents through shared entities.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive the answer.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract key information from documents (parallel processing)
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_list = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        extraction_tasks = [
            self.generate(
                instruction=f"""Extract key entities, relationships, and constraints from the following document:
                {doc}
                Format as structured data with categories: Entities, Relationships, Constraints.""",
                context=""
            ) for doc in doc_list
        ]
        extracted_info = await asyncio.gather(*extraction_tasks)

        # Step 3: Identify bridge entities (ensemble approach)
        bridge_entities = await self.ensemble(
            instruction="""Identify potential bridge entities that connect documents.
            Bridge entities are shared or logically related terms across documents.
            Provide a ranked list of candidates.""",
            contexts_list=extracted_info
        )

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities:
            {bridge_entities}
            
            Construct a reasoning chain that connects the documents to answer the question:
            {question_type}
            Ensure logical consistency and provide intermediate steps.""",
            context=""
        )

        # Step 5: Validate and refine the reasoning chain
        refined_chain = await self.revise(
            instruction=f"""Validate the reasoning chain:
            {reasoning_chain}
            
            Check for errors, fill gaps, and ensure alignment with the question requirements.
            Provide a revised version with improvements.""",
            context=reasoning_chain
        )

        # Step 6: Extract precise answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer span from the supporting documents:
            {refined_chain}
            
            Ensure the answer is factually correct and supported by the reasoning chain.
            Format as a short text span or yes/no response.""",
            context=refined_chain
        )

        return answer