# Workflow ID: hotpotqa_193_0
# Benchmark: hotpotqa
# Data Indices: [373, 484]

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

        # Step 1: Initial Analysis - Classify question type and identify key entities
        classification = await self.generate(
            instruction="""Analyze the question to determine its type:
            - Is it a bridge question (connecting entities)?
            - Is it a comparison question (comparing properties)?
            - Is it compositional (combining multiple facts)?
            Extract key entities or concepts mentioned in the question.
            Provide structured output with question type and entities.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Extract relevant facts from each document
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_texts = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        parallel_tasks = [
            self.generate(
                instruction=f"""Extract facts related to the entities or concepts identified in the initial analysis:
                {classification}
                Focus on precise details and relationships. Highlight supporting evidence.""",
                context=doc
            ) for doc in doc_texts
        ]
        document_facts = await asyncio.gather(*parallel_tasks)

        # Step 3: Summarize Extracted Facts - Condense findings for synthesis
        summarized_facts = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the extracted facts into key points relevant to the question.",
                context=fact
            ) for fact in document_facts]
        )

        # Step 4: Evidence Synthesis - Build reasoning chain and derive answer
        synthesis = await self.ensemble(
            instruction="""Synthesize the summarized facts into a coherent reasoning chain:
            - Connect entities across documents.
            - Compare properties if needed.
            - Combine multiple facts for compositional questions.
            Ensure the answer is precise and supported by evidence.""",
            contexts_list=summarized_facts
        )

        # Step 5: Validation and Refinement - Verify correctness and clarity
        refined_answer = await self.revise(
            instruction="Ensure the answer is factually correct, precise, and directly addresses the question.",
            context=synthesis
        )

        return refined_answer