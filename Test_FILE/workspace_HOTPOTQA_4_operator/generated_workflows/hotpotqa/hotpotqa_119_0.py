# Workflow ID: hotpotqa_119_0
# Benchmark: hotpotqa
# Data Indices: [123, 183]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining multiple facts)?
            Extract all named entities and their roles in the question.""",
            context=""
        )

        # Phase 2: Document Exploration
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_tasks = [
            self.generate(
                instruction=f"""For the given document:
                1. Identify mentions of the key entities extracted earlier.
                2. Highlight relationships between these entities.
                3. Summarize the document's relevance to the question.""",
                context=doc
            ) for doc in documents.split("Document ")[1:]
        ]
        doc_results = await asyncio.gather(*doc_tasks)

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction="""Using the identified bridge entities and relationships:
            1. Construct a logical chain connecting the entities across documents.
            2. Ensure each step in the chain is supported by evidence from the documents.
            3. Highlight the final entity or property that answers the question.""",
            context="\n".join(doc_results)
        )

        # Phase 4: Answer Extraction
        answer = await self.generate(
            instruction="""Based on the reasoning chain:
            1. Extract the exact text span from the documents that answers the question.
            2. If the question requires a yes/no response, determine the answer.
            Ensure the answer is factually correct and supported by evidence.""",
            context=reasoning_chain
        )

        # Phase 5: Validation and Refinement
        refined_answer = await self.revise(
            instruction="""Critique the extracted answer:
            1. Verify that it is factually correct based on the documents.
            2. Ensure it directly answers the question.
            3. Improve clarity and precision if needed.""",
            context=answer
        )

        return refined_answer