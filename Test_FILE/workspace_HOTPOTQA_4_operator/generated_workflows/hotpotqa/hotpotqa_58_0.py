# Workflow ID: hotpotqa_58_0
# Benchmark: hotpotqa
# Data Indices: [222]

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
            - Bridge questions connect entities across documents
            - Comparison questions compare properties or attributes
            - Compositional questions combine multiple facts
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities from all documents in parallel
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0]
        doc_splits = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        entity_tasks = [
            self.generate(
                instruction=f"""Extract named entities and key phrases from this document:
                {doc}""",
                context=""
            )
            for doc in doc_splits
        ]
        entities_list = await asyncio.gather(*entity_tasks)

        # Step 3: Build reasoning chains
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities:
            {entities_list}
            
            Construct a reasoning chain that connects the documents:
            - Identify shared entities
            - Map relationships between entities
            - Follow logical sequences to connect information""",
            context=question_type
        )

        # Step 4: Extract and validate the answer
        answer_candidates = []
        for doc in doc_splits:
            candidate = await self.generate(
                instruction=f"""From this document:
                {doc}
                
                Extract the precise answer that supports the reasoning chain:
                {reasoning_chain}""",
                context=""
            )
            answer_candidates.append(candidate)

        # Step 5: Ensemble decision-making
        final_answer = await self.ensemble(
            instruction="Select the most plausible answer based on supporting facts and reasoning chain consistency.",
            contexts_list=answer_candidates
        )

        return final_answer