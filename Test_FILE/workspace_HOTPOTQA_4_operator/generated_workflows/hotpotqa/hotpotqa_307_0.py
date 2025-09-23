# Workflow ID: hotpotqa_307_0
# Benchmark: hotpotqa
# Data Indices: [137]

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

        # Initial Analysis: Classify question type and identify entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and identify potential bridge entities:
            1. What is the main question?
            2. What entities are mentioned in the question?
            3. What type of reasoning is required?
            Provide structured classification.""",
            context=""
        )

        # Extract question type and entities using regex
        question_type = re.search(r'Question Type:\s*(\w+)', initial_analysis, re.IGNORECASE)
        entities = re.findall(r'Entities:\s*([\w\s,]+)', initial_analysis, re.IGNORECASE)

        # Parallel Document Analysis: Summarize each document focusing on entities
        document_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"""Summarize this document focusing on entities: {', '.join(entities)}
                - Highlight key facts about the entities
                - Identify relationships between entities
                - Note any relevant properties or characteristics""",
                context=""
            ) for _ in range(10)]  # Assuming up to 10 documents
        )

        # Bridge Entity Identification: Ensemble to find the most relevant bridge entity
        bridge_entity = await self.ensemble(
            instruction=f"""Identify the most relevant bridge entity connecting the documents:
            Entities: {', '.join(entities)}
            Summaries: {document_summaries}
            Select the entity that best connects the information across documents.""",
            contexts_list=document_summaries
        )

        # Evidence Chain Construction: Extract supporting facts for the bridge entity
        evidence_chain = []
        for summary in document_summaries:
            supporting_fact = await self.revise(
                instruction=f"""Extract supporting facts for the bridge entity: {bridge_entity}
                Summary: {summary}
                Focus on facts that directly relate to the bridge entity and contribute to answering the question.""",
                context=summary
            )
            evidence_chain.append(supporting_fact)

        # Answer Extraction: Extract precise answer from the final document
        final_answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            Bridge Entity: {bridge_entity}
            Evidence Chain: {evidence_chain}
            Ensure the answer is a short text span or a yes/no response.""",
            context=evidence_chain[-1]  # Use the last document's evidence
        )

        # Final Validation: Validate the reasoning chain and answer
        validated_answer = await self.revise(
            instruction=f"""Validate the entire reasoning chain and the extracted answer:
            Bridge Entity: {bridge_entity}
            Evidence Chain: {evidence_chain}
            Answer: {final_answer}
            Ensure the answer is factually correct and supported by the evidence chain.""",
            context=final_answer
        )

        return validated_answer