# Workflow ID: hotpotqa_321_0
# Benchmark: hotpotqa
# Data Indices: [164]

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

        # Step 1: Initial Analysis (Parallelize Question Classification and Document Filtering)
        classification_task = self.generate(
            instruction="""Classify the question type:
            - Is it a bridge question, comparison question, or compositional?
            - Identify key entities and relationships in the question.
            Provide structured output.""",
            context=""
        )
        document_filter_task = self.generate(
            instruction="""Filter relevant documents:
            - Match entities and keywords from the question against document titles and content.
            - Rank documents by relevance.
            Return a list of relevant documents.""",
            context=""
        )
        classification, filtered_docs = await asyncio.gather(classification_task, document_filter_task)

        # Step 2: Bridge Entity Detection (Conditional on Question Type)
        if "bridge" in classification.lower():
            bridge_entities = await self.generate(
                instruction=f"""Identify bridge entities:
                - Find entities that connect multiple documents.
                - Validate their presence in at least two documents.
                Relevant Documents: {filtered_docs}
                Question Context: {classification}""",
                context=""
            )
        else:
            bridge_entities = ""

        # Step 3: Reasoning Chain Construction
        reasoning_tasks = []
        for doc in filtered_docs.split("\n"):
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Extract relevant facts from this document:
                    - Focus on facts related to the question and bridge entities.
                    - Build a reasoning chain step-by-step.
                    Document: {doc}
                    Bridge Entities: {bridge_entities}""",
                    context=""
                )
            )
        reasoning_chains = await asyncio.gather(*reasoning_tasks)

        # Step 4: Ensemble Decision
        synthesized_answer = await self.ensemble(
            instruction="""Synthesize reasoning chains into a coherent answer:
            - Resolve conflicts or ambiguities.
            - Prioritize facts based on document reliability.
            - Ensure the answer directly addresses the question.""",
            contexts_list=reasoning_chains
        )

        # Step 5: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="""Extract the precise answer span:
            - Ensure the answer is factually correct and directly addresses the question.
            - Format as a short text span or yes/no response.""",
            context=synthesized_answer
        )

        return final_answer