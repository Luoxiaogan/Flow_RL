# Workflow ID: hotpotqa_149_0
# Benchmark: hotpotqa
# Data Indices: [179, 328]

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

        # Step 1: Initial Analysis - Classify question type and extract bridge entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type (bridge, comparison, compositional).
            Identify potential bridge entities that connect the documents.
            Format the output as:
            Question Type: [type]
            Bridge Entities: [list of entities]""",
            context=""
        )

        # Step 2: Document Analysis - Analyze all context documents in parallel
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for mentions of the bridge entities: {initial_analysis}.
                Identify supporting facts and their relevance to the question.""",
                context=doc
            ) for doc in self.problem_text.split('Document ')[1:]]
        )

        # Step 3: Synthesize Document Analyses - Identify most promising connections
        synthesis = await self.ensemble(
            instruction="""Synthesize the document analyses to identify the most promising connections.
            Focus on bridging entities and supporting facts that directly relate to the question.""",
            contexts_list=document_analyses
        )

        # Step 4: Reasoning Chain Construction - Build reasoning chain across documents
        reasoning_chain = await self.generate(
            instruction=f"""Using the synthesized analysis: {synthesis}
            Construct a reasoning chain that connects the documents.
            Ensure the chain is logically consistent and supported by facts.""",
            context=synthesis
        )

        # Step 5: Answer Extraction - Extract precise answer span
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer span from the reasoning chain: {reasoning_chain}.
            Ensure the answer is factually correct and matches the question format.""",
            context=reasoning_chain
        )

        # Step 6: Validation and Refinement - Validate and refine the answer
        validation = await self.revise(
            instruction=f"""Validate the extracted answer: {answer_extraction}
            Check for consistency with the reasoning chain and context documents.
            Refine if necessary.""",
            context=answer_extraction
        )

        return validation