# Workflow ID: hotpotqa_117_0
# Benchmark: hotpotqa
# Data Indices: [364, 334]

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

        # Phase 1: Problem Analysis and Classification
        problem_analysis = await self.generate(
            instruction="""Analyze the problem to classify its type:
            - Identify if it's a bridge, comparison, or compositional question.
            - Extract key entities, relationships, and constraints.
            - Provide a structured breakdown of the problem.""",
            context=""
        )

        # Determine reasoning strategy based on classification
        if "bridge" in problem_analysis.lower():
            strategy = "bridge"
        elif "comparison" in problem_analysis.lower():
            strategy = "comparison"
        else:
            strategy = "compositional"

        # Phase 2: Entity Identification and Document Linking
        entity_extraction = await self.generate(
            instruction=f"""Extract all named entities from the problem and link them to relevant documents:
            Problem Analysis: {problem_analysis}
            Instructions:
            - Identify entities mentioned in the question.
            - For each entity, find all documents where it appears.
            - Highlight the context of each mention.""",
            context=problem_analysis
        )

        # Parallel processing to analyze documents
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for mentions of the entities:
                Entities: {entity_extraction}
                Focus on extracting relevant facts and relationships.""",
                context=doc
            ) for doc in self.problem_text.split("Document ")[1:]]
        )

        # Synthesize entity-document links
        entity_links = await self.ensemble(
            instruction="Synthesize entity mentions across documents to identify bridge connections.",
            contexts_list=document_analyses
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain based on the identified entities and documents:
            Entities and Links: {entity_links}
            Strategy: {strategy}
            Instructions:
            - Start with the primary entity.
            - Follow connections to other entities and documents.
            - Build a logical chain leading to the answer.""",
            context=entity_links
        )

        # Refine the reasoning chain iteratively
        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity, coherence, and completeness.",
            context=reasoning_chain
        )

        # Phase 4: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Refined Chain: {refined_chain}
            Instructions:
            - Identify the final answer span.
            - Ensure it is factually correct and supported by the documents.
            - Provide supporting facts.""",
            context=refined_chain
        )

        final_answer = await self.summarize(
            instruction="Condense the answer into a concise, factual response.",
            context=answer_extraction
        )

        return final_answer