# Workflow ID: hotpotqa_138_0
# Benchmark: hotpotqa
# Data Indices: [176]

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

        # Step 1: Initial Analysis - Classify question type and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities, relationships, and constraints.
            3. Provide a structured summary of the problem.""",
            context=""
        )

        # Step 2: Parallel Entity Extraction - Extract entities from each document
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_texts = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        entity_extraction_tasks = [
            self.generate(
                instruction=f"Extract named entities, relationships, and key phrases from this document:\n{doc}",
                context=""
            ) for doc in doc_texts
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Merge extracted entities into a unified map
        unified_entity_map = await self.ensemble(
            instruction="Merge extracted entities into a unified map, highlighting overlaps and potential bridge entities.",
            contexts_list=extracted_entities
        )

        # Step 3: Reasoning Chain Construction - Build explicit reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the unified entity map:
            {unified_entity_map}
            
            Construct a reasoning chain that connects the question to the final answer:
            1. Identify bridge entities that connect documents.
            2. Trace the logical flow from the question through intermediate facts to the conclusion.
            3. Ensure each step is grounded in the provided documents.""",
            context=initial_analysis
        )

        # Iterative refinement of reasoning chain
        for _ in range(3):  # Allow up to 3 iterations for refinement
            validation = await self.generate(
                instruction="Validate the reasoning chain for logical consistency and completeness.",
                context=reasoning_chain
            )
            if "error" in validation.lower():
                reasoning_chain = await self.revise(
                    instruction=f"Fix issues in the reasoning chain: {validation}",
                    context=reasoning_chain
                )
            else:
                break

        # Step 4: Answer Extraction - Extract precise answer from relevant document
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the relevant document. Ensure the answer is factually correct and directly addresses the question.""",
            context=""
        )

        # Validate the extracted answer
        validation = await self.generate(
            instruction=f"Cross-check the extracted answer against the reasoning chain:\n{answer_extraction}",
            context=reasoning_chain
        )
        if "inconsistent" in validation.lower():
            answer_extraction = await self.revise(
                instruction=f"Revise the extracted answer to address inconsistencies: {validation}",
                context=answer_extraction
            )

        # Step 5: Final Synthesis - Combine results into concise output
        final_output = await self.ensemble(
            instruction="""Synthesize all intermediate results into a concise output:
            1. Include the final answer.
            2. Summarize the reasoning chain.
            3. Highlight supporting facts from different documents.""",
            contexts_list=[initial_analysis, unified_entity_map, reasoning_chain, answer_extraction]
        )

        return final_output