# Workflow ID: hotpotqa_173_0
# Benchmark: hotpotqa
# Data Indices: [494]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and extract key entities that connect documents. Identify potential bridge entities 
            and relationships between them. Format output as:
            Question Type: [type]
            Key Entities: [list of entities]""",
            context=""
        )

        # Parse initial analysis
        question_type = re.search(r"Question Type:\s*(\w+)", initial_analysis).group(1)
        key_entities = re.findall(r"Key Entities:\s*([\w\s,]+)", initial_analysis)[0].split(", ")

        # Step 2: Relevance Scoring - Score each document's relevance to the question and entities
        documents = re.findall(r"Document \d+: (.+?)\n", self.problem_text, re.DOTALL)
        relevance_scores = await asyncio.gather(
            *[self.generate(
                instruction=f"""Score this document's relevance to the question and entities: {key_entities}.
                Provide a relevance score from 0 to 10, where 10 is highly relevant.""",
                context=doc
            ) for doc in documents]
        )

        # Filter top 3 most relevant documents
        top_docs = sorted(zip(documents, relevance_scores), key=lambda x: int(re.search(r"\d+", x[1]).group()), reverse=True)[:3]
        relevant_documents = [doc for doc, _ in top_docs]

        # Step 3: Reasoning Chain Construction - Build reasoning chain across documents
        reasoning_chain = ""
        for i, doc in enumerate(relevant_documents):
            step = await self.generate(
                instruction=f"""Using this document and the previous reasoning chain:
                Previous Chain: {reasoning_chain}
                Current Document: {doc}
                
                Extract supporting facts and connect them to the reasoning chain. Focus on the key entities: {key_entities}.""",
                context=doc
            )
            reasoning_chain += step + "\n"

        # Step 4: Answer Extraction and Validation - Extract and validate the answer
        extracted_answer = await self.summarize(
            instruction="Extract the precise answer from the reasoning chain. Ensure it is concise and factual.",
            context=reasoning_chain
        )

        validation_result = await self.ensemble(
            instruction="Validate the extracted answer against the supporting facts. Ensure factual accuracy.",
            contexts_list=[extracted_answer, reasoning_chain]
        )

        # Feedback Loop: Refine if validation fails
        if "error" in validation_result.lower():
            refined_answer = await self.revise(
                instruction=f"Refine the answer based on validation feedback: {validation_result}",
                context=extracted_answer
            )
            return refined_answer

        return extracted_answer