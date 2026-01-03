# Workflow ID: hotpotqa_108_0
# Benchmark: hotpotqa
# Data Indices: [151, 338]

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
            instruction="""Analyze the question to determine its type and extract key entities:
            - Is it a bridge question, comparison question, or compositional question?
            - Identify the main entities involved.
            - Provide a structured classification.""",
            context=""
        )

        # Phase 2: Document Filtering
        entities = await self.generate(
            instruction="Extract all named entities from the analysis.",
            context=analysis
        )
        filtered_docs = await asyncio.gather(
            *[self.generate(
                instruction=f"Does this document contain information about {entities}?",
                context=doc
            ) for doc in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document")]
        )
        relevant_docs = [doc for doc, relevant in zip(self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document"), filtered_docs) if "yes" in relevant.lower()]

        # Phase 3: Fact Extraction and Reasoning
        extracted_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract sentences containing {entities} and their relevant properties.",
                context=doc
            ) for doc in relevant_docs]
        )
        refined_facts = await asyncio.gather(
            *[self.revise(
                instruction="Refine extracted facts to ensure clarity and relevance.",
                context=fact
            ) for fact in extracted_facts]
        )

        # Phase 4: Answer Synthesis
        answer = await self.ensemble(
            instruction="Combine the refined facts to answer the question. Ensure the answer is concise and factually correct.",
            contexts_list=refined_facts
        )

        return answer