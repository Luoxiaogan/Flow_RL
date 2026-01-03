# Workflow ID: hotpotqa_231_0
# Benchmark: hotpotqa
# Data Indices: [129]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships mentioned in the question.
            3. Identify potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Extract entities and relationships from all documents
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document:
                1. Extract all named entities (people, places, events).
                2. Identify relationships between entities.
                3. Highlight potential bridge entities that match the question.
                Document content: {doc}""",
                context=initial_analysis
            ) for doc in self.extract_documents()]
        )

        # Step 3: Entity Matching - Identify shared entities across documents
        shared_entities = await self.ensemble(
            instruction="""Identify shared entities (bridge entities) that connect documents:
            1. Compare entities extracted from all documents.
            2. Select entities that are most relevant to the question.
            3. Provide a ranked list of bridge entities.""",
            contexts_list=document_analyses
        )

        # Step 4: Reasoning Chain Construction - Build logical connections
        reasoning_chain = await self.generate(
            instruction=f"""Using the shared entities:
            {shared_entities}
            
            Build a reasoning chain:
            1. Connect entities across documents logically.
            2. Follow the chain to locate the document containing the answer.
            3. Provide a detailed explanation of the reasoning process.""",
            context=shared_entities
        )

        # Step 5: Iterative Refinement - Improve reasoning chain if necessary
        refined_chain = reasoning_chain
        for _ in range(2):  # Allow up to 2 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                {refined_chain}
                
                Check for logical consistency and completeness.
                Identify any gaps or ambiguities.""",
                context=refined_chain
            )
            if "gap" in validation.lower() or "ambiguity" in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"""Refine the reasoning chain:
                    Address the following issues: {validation}""",
                    context=refined_chain
                )
            else:
                break

        # Step 6: Answer Extraction - Locate precise answer span
        answer_extraction = await self.generate(
            instruction=f"""Using the refined reasoning chain:
            {refined_chain}
            
            Extract the precise answer span from the relevant document.
            Provide the exact text and its location in the document.""",
            context=refined_chain
        )

        # Step 7: Validation - Verify answer against supporting facts
        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            {answer_extraction}
            
            Ensure it aligns with the supporting facts from the documents.
            Address any discrepancies.""",
            context=answer_extraction
        )

        return validated_answer

    def extract_documents(self):
        """Helper method to extract document content from problem text."""
        # Placeholder implementation - replace with actual parsing logic
        return ["Document 1 content", "Document 2 content", "Document 3 content"]