# Workflow ID: hotpotqa_330_0
# Benchmark: hotpotqa
# Data Indices: [432]

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
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and extract key entities. Provide structured output:
            - Question Type: [type]
            - Entities: [list of entities]""",
            context=""
        )

        # Phase 2: Document Filtering
        relevant_docs = await self.generate(
            instruction=f"""Identify documents containing information about the entities:
            {analysis}
            
            List document titles and relevant sections.""",
            context=""
        )

        # Phase 3: Fact Extraction (Parallel Processing)
        doc_facts = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Extract key facts about the entities from this document:
                {doc}""",
                context=doc
            ) for doc in relevant_docs.split("\n") if doc.strip()]
        )

        # Phase 4: Reasoning Chain Construction
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize the extracted facts into a logical chain:
            - Connect facts across documents
            - Ensure coherence and relevance to the question""",
            contexts_list=doc_facts
        )

        # Phase 5: Answer Synthesis
        initial_answer = await self.generate(
            instruction=f"""Based on the reasoning chain:
            {reasoning_chain}
            
            Generate the final answer in short text format.""",
            context=reasoning_chain
        )

        refined_answer = await self.revise(
            instruction="""Refine the answer for clarity, precision, and factual accuracy.
            Ensure it matches the expected format (short text spans or yes/no).""",
            context=initial_answer
        )

        return refined_answer