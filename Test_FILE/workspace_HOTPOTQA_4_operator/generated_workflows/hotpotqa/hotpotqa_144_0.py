# Workflow ID: hotpotqa_144_0
# Benchmark: hotpotqa
# Data Indices: [406, 269]

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

        # Phase 1: Question Classification and Entity Extraction
        analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - Identify entities mentioned in the question.
            - Determine relationships between entities.
            - Classify the question type based on its structure.
            Provide structured output with clear labels.""",
            context=""
        )

        # Phase 2: Parallel Exploration of Documents
        entities = [entity.strip() for entity in analysis.split("\n") if "entity:" in entity.lower()]
        document_tasks = [
            self.generate(
                instruction=f"""Find documents containing the entity '{entity}' and extract supporting facts:
                - List relevant documents.
                - Highlight sentences mentioning the entity.
                - Identify relationships involving the entity.""",
                context=""
            )
            for entity in entities
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Phase 3: Document Linking and Reasoning Chain Construction
        selected_documents = await self.ensemble(
            instruction="""Select the most relevant documents and construct a reasoning chain:
            - Prioritize documents with strong entity connections.
            - Build a logical chain by connecting documents through shared entities.
            - Ensure the chain leads to the final answer.""",
            contexts_list=document_results
        )

        # Phase 4: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            - Use the question to guide extraction.
            - Ensure the answer is factually correct and concise.
            Selected Documents: {selected_documents}""",
            context=""
        )

        # Phase 5: Validation and Refinement
        validation = await self.revise(
            instruction=f"""Validate the answer against the question and refine if necessary:
            - Check factual accuracy.
            - Ensure the answer format matches the question requirements.
            - Correct any errors or ambiguities.
            Answer: {answer}""",
            context=selected_documents
        )

        # Final Output
        return validation