# Workflow ID: hotpotqa_110_0
# Benchmark: hotpotqa
# Data Indices: [88]

import asyncio

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
        import re

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge Questions: Connect documents through shared entities (e.g., "What nationality is the director of [movie]?").
            2. Comparison Questions: Compare properties across documents (e.g., "Which was founded first, X or Y?").
            3. Compositional Questions: Combine multiple facts to derive an answer.
            Provide a clear classification and explain your reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents (parallelized)
        documents = re.findall(r"Document \d+:.*?(?=\n\n|$)", self.problem_text, re.DOTALL)
        entity_extractions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all named entities, relationships, and key facts from the following document:
                {doc}
                Format as a structured list with categories:
                - Entities: [names and roles]
                - Relationships: [connections between entities]
                - Key Facts: [important details]""",
                context=""
            ) for doc in documents]
        )

        # Step 3: Build the reasoning chain
        reasoning_chain = ""
        for i, entities in enumerate(entity_extractions):
            reasoning_step = await self.generate(
                instruction=f"""Using the extracted entities and relationships from Document {i+1}:
                {entities}
                
                Connect these to the overall reasoning chain:
                {reasoning_chain}
                
                Identify any bridge entities or relevant facts that help answer the question:
                {question_type}""",
                context=reasoning_chain
            )
            reasoning_chain += f"\nStep {i+1}: {reasoning_step}"
        
        # Step 4: Extract the answer
        extracted_answer = await self.generate(
            instruction=f"""Based on the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer from the relevant document. Ensure the answer is a short text span or yes/no response.""",
            context=""
        )

        # Step 5: Validate and refine the answer
        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer against the reasoning chain:
            {reasoning_chain}
            
            Ensure the answer is factually correct, directly supported by the documents, and matches the expected format.""",
            context=extracted_answer
        )

        return validated_answer