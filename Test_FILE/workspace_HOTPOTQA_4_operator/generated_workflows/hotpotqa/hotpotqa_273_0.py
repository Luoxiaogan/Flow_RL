# Workflow ID: hotpotqa_273_0
# Benchmark: hotpotqa
# Data Indices: [472, 225]

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

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question type:
            - Bridge questions connect entities across documents.
            - Comparison questions compare properties or attributes.
            - Compositional questions combine multiple facts.
            Provide a clear classification and explanation.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities and relationships from the following document:
                {doc}
                Format as a structured list of entities and their relationships.""",
                context=""
            ) for doc in self.extract_documents()
        ]
        entities_and_relationships = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Link documents through shared entities
        document_links = await self.ensemble(
            instruction="""Identify shared entities or overlapping relationships across documents.
            Prioritize connections that are most relevant to the question.""",
            contexts_list=entities_and_relationships
        )

        # Step 4: Construct the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the document links:
            {document_links}
            Construct a reasoning chain that connects the question to the answer.
            Validate each step against the source documents.""",
            context=question_type
        )
        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity and accuracy.",
            context=reasoning_chain
        )

        # Step 5: Extract the precise answer
        answer = await self.generate(
            instruction=f"""From the reasoning chain:
            {refined_chain}
            Extract the precise answer span from the final document.
            Ensure the answer is factually correct and directly supported by evidence.""",
            context=""
        )

        return answer

    def extract_documents(self):
        # Helper function to extract individual documents from the problem text
        sections = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        return [section.strip() for section in sections if section.strip()]