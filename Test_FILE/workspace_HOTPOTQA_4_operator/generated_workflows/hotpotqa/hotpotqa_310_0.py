# Workflow ID: hotpotqa_310_0
# Benchmark: hotpotqa
# Data Indices: [337]

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

        # Step 1: Initial Analysis - Classify Question Type and Identify Key Entities
        classification = await self.generate(
            instruction="""Classify the question type and identify key entities or properties:
            - Is it a bridge, comparison, or compositional question?
            - What entities or properties are central to the question?
            - What documents might contain relevant information?""",
            context=""
        )

        # Step 2: Parallel Document Processing - Extract Relevant Information
        document_entities = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all entities, relationships, and key facts from this document:
                Focus on entities related to: {classification}""",
                context=document
            ) for document in self._extract_documents()]
        )

        # Step 3: Reasoning Chain Construction - Build Connections Across Documents
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            - Build a reasoning chain that connects the documents.
            - Ensure the chain logically leads to the answer.
            Entities: {document_entities}""",
            context=classification
        )

        # Step 4: Answer Extraction - Extract Precise Answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            - Ensure the answer is factually correct.
            - Provide exact text spans or yes/no responses.
            Reasoning Chain: {reasoning_chain}""",
            context=document_entities[-1]
        )

        # Step 5: Validation and Refinement - Validate Reasoning Chain and Refine Answer
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain and answer:
            - Is the chain complete and logical?
            - Does the answer match the question?
            Reasoning Chain: {reasoning_chain}
            Answer: {answer}""",
            context=classification
        )

        refined_answer = await self.revise(
            instruction=f"""Refine the answer based on validation feedback:
            - Address any gaps or ambiguities.
            - Ensure precision and factual correctness.
            Validation Feedback: {validation}""",
            context=answer
        )

        return refined_answer

    def _extract_documents(self):
        """Helper method to extract individual documents from the problem text."""
        import re
        pattern = r"Document \d+:.*?\n(.*?)(?=\n\n|$)"
        return re.findall(pattern, self.problem_text, re.DOTALL)