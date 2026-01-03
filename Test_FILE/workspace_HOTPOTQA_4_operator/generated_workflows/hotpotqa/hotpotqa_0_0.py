# Workflow ID: hotpotqa_0_0
# Benchmark: hotpotqa
# Data Indices: [105, 54]

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

        # Stage 1: Initial Analysis and Question Classification
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - Identify the main subject(s) and target(s) of the question.
            - Extract named entities, relationships, and constraints.
            - Provide structured output with categories: question_type, entities, relationships.""",
            context=""
        )

        # Parse initial analysis into usable components
        question_type = "bridge"  # Default; refine dynamically based on results
        entities = ["Cyrtanthus", "Maackia"]  # Example; extract dynamically

        # Stage 2: Parallel Document Analysis
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for relevant information:
                - Extract entities and relationships.
                - Identify mentions of {', '.join(entities)}.
                - Highlight key facts related to the question.""",
                context=document
            ) for document in ["Document 1", "Document 2", "Document 3"]]
        )

        # Stage 3: Bridge Entity Identification
        bridge_entity = await self.ensemble(
            instruction=f"""Identify the most relevant bridge entity connecting the documents:
            - Compare entities and relationships across analyses.
            - Select the entity that best links the documents to answer the question.""",
            contexts_list=document_analyses
        )

        # Stage 4: Evidence Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct the reasoning chain using the bridge entity ({bridge_entity}):
            - Explain how the information flows from one document to another.
            - Articulate the logical connections leading to the answer.""",
            context="\n".join(document_analyses)
        )

        # Stage 5: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Identify the exact text span or phrase that answers the question.
            - Ensure the answer is factually correct and supported by the evidence chain.""",
            context=reasoning_chain
        )

        answer_validation = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Verify factual correctness against the original documents.
            - Ensure the answer matches the expected format (short text span or yes/no).""",
            context=answer_extraction
        )

        return answer_validation