# Workflow ID: hotpotqa_56_0
# Benchmark: hotpotqa
# Data Indices: [435, 466]

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
            instruction="""Classify the question type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Extract named entities (people, organizations, dates) and their relationships.
            - Identify constraints or conditions in the question.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Document Analysis
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document ")[1:]
        document_tasks = [
            self.generate(
                instruction=f"""Analyze this document for relevance to the question:
                - Extract information related to the identified entities.
                - Highlight key facts and relationships.
                Document Content: {doc}""",
                context=analysis
            ) for doc in documents
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted information from all documents:
            - Identify 'bridge entities' that connect documents.
            - Build a logical sequence of relationships between entities.
            - Construct a reasoning chain that answers the question.
            Document Analyses: {document_results}""",
            context=analysis
        )

        # Step 4: Validation and Refinement
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain against the documents:
            - Check for factual consistency.
            - Identify any missing or inconsistent information.
            Reasoning Chain: {reasoning_chain}""",
            context="\n".join(document_results)
        )
        if "inconsistent" in validation.lower() or "missing" in validation.lower():
            refined_chain = await self.revise(
                instruction=f"""Refine the reasoning chain based on validation feedback:
                Feedback: {validation}
                Original Chain: {reasoning_chain}""",
                context=reasoning_chain
            )
            reasoning_chain = refined_chain

        # Step 5: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Ensure the answer is factually correct and matches the expected format.
            - If the question requires a yes/no response, determine the answer based on the chain.
            Reasoning Chain: {reasoning_chain}""",
            context=validation
        )

        return answer