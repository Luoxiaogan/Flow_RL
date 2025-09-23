# Workflow ID: hotpotqa_186_0
# Benchmark: hotpotqa
# Data Indices: [90, 60]

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

        # Step 1: Initial Analysis - Classify question type and identify key terms
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and identify potential bridge entities or key terms:
            - What entities or concepts are central to the question?
            - Which documents might contain relevant information?
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Document Filtering - Narrow down relevant documents
        filtered_documents = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Filter the documents to those most relevant to the question:
            - Which documents mention the key terms or bridge entities?
            - Prioritize documents with direct connections to the question.""",
            context=initial_analysis
        )

        # Step 3: Sentence Extraction - Extract relevant sentences from filtered documents
        extracted_sentences = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract sentences containing the key terms or bridge entities from this document:
                {doc}""",
                context=filtered_documents
            ) for doc in filtered_documents.split("\n\n") if doc.strip()]
        )
        combined_sentences = "\n".join(extracted_sentences)

        # Step 4: Reasoning Chain Construction - Build logical connections
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain using these sentences:
                {sentences}
                
                Ensure logical consistency and connect the information across documents.""",
                context=combined_sentences
            ) for sentences in extracted_sentences]
        )

        # Step 5: Ensemble - Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains and select the most coherent and factually supported one:
            - Does the chain logically connect the documents?
            - Is it supported by the evidence in the text?""",
            contexts_list=reasoning_chains
        )

        # Step 6: Answer Extraction - Extract precise answer span
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer span from the reasoning chain:
            {best_chain}
            
            Ensure the answer is a short, factual span directly from the text.""",
            context=best_chain
        )

        # Step 7: Validation - Verify the answer
        validated_answer = await self.revise(
            instruction=f"""Verify the answer:
            {answer_extraction}
            
            Ensure it is factually correct and supported by the reasoning chain.""",
            context=answer_extraction
        )

        return validated_answer