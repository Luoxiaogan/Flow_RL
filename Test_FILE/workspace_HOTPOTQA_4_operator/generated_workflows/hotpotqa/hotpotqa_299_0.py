# Workflow ID: hotpotqa_299_0
# Benchmark: hotpotqa
# Data Indices: [146]

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

        # Step 1: Parallel Entity Extraction
        async def extract_entities(doc_id):
            return await self.generate(
                instruction=f"""
                Extract all named entities, temporal markers, and relationships from Document {doc_id}.
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )

        # Extract entities from all documents in parallel
        entity_extraction_tasks = [extract_entities(i) for i in range(1, 11)]  # Assuming 10 documents
        entity_results = await asyncio.gather(*entity_extraction_tasks)

        # Step 2: Identify Bridge Entities
        bridge_entity_candidates = await self.ensemble(
            instruction="""
            Compare the extracted entities across documents to find overlaps or semantic connections.
            Select the most relevant bridge entity that connects the documents and aligns with the question.""",
            contexts_list=entity_results
        )

        # Step 3: Construct Reasoning Chain
        reasoning_chain = await self.generate(
            instruction=f"""
            Using the bridge entity: {bridge_entity_candidates}
            Construct a reasoning chain by linking facts from different documents.
            Ensure the chain is coherent and factually accurate, addressing the question directly.""",
            context="\n".join(entity_results)
        )

        # Step 4: Extract Precise Answer
        answer_extraction = await self.generate(
            instruction=f"""
            From the reasoning chain: {reasoning_chain}
            Extract the precise answer span that directly answers the question.
            Ensure the answer is short, factual, and directly from the text.""",
            context=reasoning_chain
        )

        # Step 5: Iterative Refinement
        refined_answer = await self.revise(
            instruction=f"""
            Review the extracted answer: {answer_extraction}
            Refine it for clarity, precision, and factual accuracy.
            Ensure it aligns with the reasoning chain and supporting facts.""",
            context=answer_extraction
        )

        # Step 6: Summarize Supporting Facts
        summary = await self.summarize(
            instruction=f"""
            Summarize the reasoning chain and supporting facts:
            {reasoning_chain}
            Focus on key points that validate the answer.""",
            context=reasoning_chain
        )

        # Final Output
        return {
            "answer": refined_answer,
            "supporting_facts": summary
        }