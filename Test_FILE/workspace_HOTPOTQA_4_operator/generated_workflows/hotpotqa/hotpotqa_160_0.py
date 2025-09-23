# Workflow ID: hotpotqa_160_0
# Benchmark: hotpotqa
# Data Indices: [217, 3]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        analysis = await self.generate(
            instruction="""Analyze the problem and classify its type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. Extract all named entities, numbers, and relationships.
            3. Identify potential bridge entities that connect documents.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Identify relevant information in each document
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_list = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        parallel_tasks = [
            self.generate(
                instruction=f"""Analyze this document:
                - Extract key entities and relationships.
                - Highlight mentions of bridge entities identified earlier.
                - Summarize relevant information for answering the question.
                Document content: {doc}""",
                context=analysis
            )
            for doc in doc_list
        ]
        doc_analyses = await asyncio.gather(*parallel_tasks)

        # Step 3: Entity Connection - Resolve ambiguities and identify reasoning chains
        entity_connections = await self.ensemble(
            instruction="""Synthesize information from all documents:
            - Identify the most likely bridge entities.
            - Resolve ambiguities in entity matching.
            - Build initial reasoning chains connecting documents.""",
            contexts_list=doc_analyses
        )

        # Step 4: Reasoning Chain Construction - Follow logical connections
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities and connections:
            {entity_connections}
            
            Construct a detailed reasoning chain:
            - Follow logical connections across documents.
            - Ensure each step is supported by evidence.
            - Identify the final document containing the answer.""",
            context=entity_connections
        )

        # Step 5: Answer Extraction - Extract precise answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the final document:
            Reasoning chain: {reasoning_chain}
            
            - Locate the exact sentence or phrase containing the answer.
            - Ensure the answer matches the question format.
            - Validate factual correctness.""",
            context=reasoning_chain
        )

        # Step 6: Final Validation - Refine and summarize the answer
        refined_answer = await self.revise(
            instruction="""Refine the extracted answer:
            - Improve clarity and precision.
            - Ensure it directly addresses the question.
            - Add supporting evidence if necessary.""",
            context=answer_extraction
        )

        final_answer = await self.summarize(
            instruction="Condense the refined answer into a short, factual response.",
            context=refined_answer
        )

        return final_answer