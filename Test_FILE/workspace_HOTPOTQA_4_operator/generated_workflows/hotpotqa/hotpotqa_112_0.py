# Workflow ID: hotpotqa_112_0
# Benchmark: hotpotqa
# Data Indices: [463]

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
        import re

        # Step 1: Classify the question type
        classification = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (evaluating properties of entities)?
            3. Is it a compositional question (combining multiple facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all relevant entities and their relationships:
            Classification: {classification}
            
            Format as structured list:
            - Entities: [names and roles]
            - Relationships: [connections between entities]""",
            context=""
        )

        # Step 3: Analyze documents in parallel
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for relevant information:
                Entities: {entities}
                
                Focus on facts that connect to the entities.""",
                context=document
            ) for document in re.findall(r"Document \d+:.*?(?=\n\nDocument|\Z)", self.problem_text, re.DOTALL)]
        )

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain connecting the entities:
            Classification: {classification}
            Entities: {entities}
            Document Analyses: {document_analyses}
            
            Follow the relationships between entities to arrive at the answer.""",
            context=""
        )

        # Step 5: Extract and validate answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the exact answer span from the documents:
            Reasoning Chain: {reasoning_chain}
            
            Ensure the answer is factually correct and supported by the documents.""",
            context=""
        )

        # Step 6: Ensemble decision for final answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the results and select the best answer:
            Consider all analyses and reasoning chains.
            Prioritize answers supported by multiple documents.""",
            contexts_list=[classification, entities, reasoning_chain, answer_extraction]
        )

        return final_answer