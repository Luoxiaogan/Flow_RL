# Workflow ID: hotpotqa_135_0
# Benchmark: hotpotqa
# Data Indices: [136, 221]

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
        
        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional).
            Extract key entities and relationships mentioned in the question.
            Provide structured output with clear labels.""",
            context=""
        )
        
        # Step 2: Document Analysis
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for mentions of key entities:
                {initial_analysis}
                Extract relationships and supporting facts.
                Provide concise summary.""",
                context=doc
            ) for doc in documents.split("Document ")[1:]]
        )
        
        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.ensemble(
            instruction="""Identify connections between documents using extracted entities.
            Construct a logical reasoning chain linking documents.
            Ensure all steps are supported by evidence.""",
            contexts_list=doc_summaries
        )
        
        # Step 4: Answer Extraction
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            Extract the precise answer span from the relevant document.
            Ensure the answer is factually correct and directly answers the question.""",
            context=""
        )
        
        # Step 5: Final Output
        final_output = await self.summarize(
            instruction="""Summarize the reasoning chain and answer.
            Include the short text answer and supporting facts.
            Format clearly for readability.""",
            context=f"{reasoning_chain}

{answer_extraction}"
        )
        
        return final_output