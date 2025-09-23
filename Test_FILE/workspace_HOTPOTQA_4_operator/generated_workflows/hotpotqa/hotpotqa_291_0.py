# Workflow ID: hotpotqa_291_0
# Benchmark: hotpotqa
# Data Indices: [376]

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
        question_analysis = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting entities across documents (e.g., "What nationality is the director of [movie]?")
            - Comparison: Requires comparing properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional: Requires combining multiple facts to derive the answer
            Provide a clear classification and explain your reasoning.""",
            context=""
        )

        # Step 2: Extract entities and map to documents (parallel processing)
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        document_texts = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        
        async def process_document(doc):
            return await self.generate(
                instruction=f"""Extract all named entities, numbers, and relationships from this document:
                {doc}
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )
        
        entity_results = await asyncio.gather(*[process_document(doc) for doc in document_texts])

        # Step 3: Build reasoning chain based on question type
        if "Bridge" in question_analysis:
            reasoning_chain = await self.generate(
                instruction=f"""Using the extracted entities:
                {entity_results}
                
                Identify shared entities across documents and construct a reasoning chain to connect them.
                Provide a step-by-step explanation of how the entities relate to each other.""",
                context=question_analysis
            )
        elif "Comparison" in question_analysis:
            reasoning_chain = await self.generate(
                instruction=f"""Using the extracted entities:
                {entity_results}
                
                Compare properties across documents and construct a reasoning chain to evaluate the question.
                Provide a step-by-step explanation of how the properties relate to each other.""",
                context=question_analysis
            )
        else:  # Compositional
            reasoning_chain = await self.generate(
                instruction=f"""Using the extracted entities:
                {entity_results}
                
                Combine multiple facts to construct a reasoning chain.
                Provide a step-by-step explanation of how the facts relate to each other.""",
                context=question_analysis
            )

        # Step 4: Extract and validate the answer
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer from the documents. Ensure it is an exact span of text and factually correct.
            Provide the answer and supporting facts.""",
            context=""
        )

        # Step 5: Refine the answer
        refined_answer = await self.revise(
            instruction="Ensure the answer is precise, factual, and directly addresses the question.",
            context=answer_extraction
        )

        return refined_answer