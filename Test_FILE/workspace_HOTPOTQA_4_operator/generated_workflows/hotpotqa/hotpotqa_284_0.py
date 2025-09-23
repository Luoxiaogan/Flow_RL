# Workflow ID: hotpotqa_284_0
# Benchmark: hotpotqa
# Data Indices: [224]

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
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships mentioned in the question.
            3. Provide a structured breakdown of the problem.""",
            context=""
        )
        
        # Step 2: Entity and Relationship Extraction
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities and relationships from the following document:
                {doc}""",
                context=""
            ) for doc in documents.split("Document ")[1:]
        ]
        extracted_data = await asyncio.gather(*extraction_tasks)
        
        # Step 3: Identify Bridge Entities
        bridge_entities = await self.ensemble(
            instruction="""Identify the most relevant bridge entities that connect the documents:
            - Prioritize entities mentioned in the question.
            - Ensure entities appear in multiple documents.
            - Rank entities by relevance to the question.""",
            contexts_list=extracted_data
        )
        
        # Step 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain using the bridge entities:
            Bridge Entities: {bridge_entities}
            Documents: {documents}
            
            Follow the trail of shared entities to connect documents and extract supporting facts.""",
            context=""
        )
        
        # Step 5: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            
            Ensure the answer is factually correct and matches the question format.""",
            context=""
        )
        
        # Step 6: Validation and Feedback Loop
        validation = await self.revise(
            instruction=f"""Validate the answer against the supporting facts:
            Answer: {answer}
            Supporting Facts: {reasoning_chain}
            
            If invalid, suggest improvements or indicate missing information.""",
            context=answer
        )
        
        if "invalid" in validation.lower():
            # Revisit earlier steps to refine the reasoning chain
            refined_chain = await self.revise(
                instruction=f"""Refine the reasoning chain based on validation feedback:
                Feedback: {validation}
                Original Chain: {reasoning_chain}""",
                context=reasoning_chain
            )
            answer = await self.generate(
                instruction=f"""Extract the precise answer from the refined reasoning chain:
                Refined Chain: {refined_chain}""",
                context=""
            )
        
        return answer