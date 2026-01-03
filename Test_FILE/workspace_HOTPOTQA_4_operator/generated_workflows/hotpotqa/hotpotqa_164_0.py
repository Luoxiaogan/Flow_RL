# Workflow ID: hotpotqa_164_0
# Benchmark: hotpotqa
# Data Indices: [124]

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
        
        # Step 1: Problem Decomposition
        analysis = await self.generate(
            instruction="""Analyze the problem to:
            - Identify the question type (e.g., bridge, comparison, compositional).
            - Extract key entities and their roles (e.g., people, places, organizations).
            - Highlight relationships between entities (e.g., 'director of').
            - Note any constraints or conditions (e.g., 'released after 2000').
            Provide structured output with clear categories.""",
            context=""
        )
        refined_analysis = await self.revise(
            instruction="Refine the analysis to ensure accuracy and completeness.",
            context=analysis
        )
        
        # Step 2: Document Linking
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_tasks = []
        for doc in documents.split("Document ")[1:]:
            title, content = doc.split("\n", 1)
            doc_tasks.append(
                self.generate(
                    instruction=f"""Scan this document for mentions of key entities from the analysis:
                    - Extract sentences or paragraphs describing the entities.
                    - Summarize the relevant information into concise facts.
                    Document Title: {title}
                    Content: {content}""",
                    context=refined_analysis
                )
            )
        doc_results = await asyncio.gather(*doc_tasks)
        relevant_docs = await self.ensemble(
            instruction="Select the documents most relevant to the question based on supporting evidence.",
            contexts_list=doc_results
        )
        
        # Step 3: Reasoning Chain Construction
        reasoning_chain = ""
        for doc in relevant_docs.split("\n"):
            step = await self.generate(
                instruction=f"""Using the previous reasoning step: {reasoning_chain}
                Connect this document to the chain by identifying shared entities and relationships.
                Document: {doc}""",
                context=reasoning_chain
            )
            reasoning_chain += step + "\n"
        
        # Step 4: Answer Extraction and Validation
        answer = await self.summarize(
            instruction="""Extract the precise answer from the final document in the reasoning chain.
            Ensure the answer matches the expected format and constraints.""",
            context=reasoning_chain
        )
        validated_answer = await self.revise(
            instruction="Validate the answer against the documents to ensure factual correctness.",
            context=answer
        )
        
        return validated_answer