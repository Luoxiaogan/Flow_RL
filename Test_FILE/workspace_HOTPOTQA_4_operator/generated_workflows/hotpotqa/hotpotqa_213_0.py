# Workflow ID: hotpotqa_213_0
# Benchmark: hotpotqa
# Data Indices: [2]

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

        # Step 1: Initial Analysis - Classify question type and identify key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify its type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. Identify key entities mentioned in the question.
            3. Highlight any specific constraints or conditions.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Entity Extraction - Extract entities and relationships from all documents
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_list = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        
        async def extract_entities(doc):
            return await self.generate(
                instruction=f"""Extract all named entities, relationships, and key facts from this document:
                {doc}
                Focus on entities relevant to the question type identified earlier.""",
                context=initial_analysis
            )
        
        entity_extractions = await asyncio.gather(*[extract_entities(doc) for doc in doc_list])

        # Step 3: Reasoning Chain Construction - Build logical chains connecting documents
        reasoning_chains = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {entity_extractions}
            
            Construct reasoning chains that connect the documents:
            - Identify shared entities or concepts.
            - Trace logical connections between documents.
            - Highlight potential answer candidates.""",
            context=initial_analysis
        )

        # Step 4: Answer Extraction and Validation - Extract precise answers and validate
        answer_candidates = await self.generate(
            instruction=f"""From the reasoning chains:
            {reasoning_chains}
            
            Extract precise answer spans from the documents:
            - Ensure answers are factually correct.
            - Validate against supporting facts from multiple documents.""",
            context=reasoning_chains
        )

        # Step 5: Final Synthesis - Combine insights into a concise response
        final_answer = await self.revise(
            instruction=f"""Refine the answer candidates:
            {answer_candidates}
            
            Select the most accurate and concise response:
            - Ensure it matches the question type.
            - Verify against supporting facts.
            - Present the final answer in the required format.""",
            context=answer_candidates
        )

        return final_answer