# Workflow ID: hotpotqa_1_0
# Benchmark: hotpotqa
# Data Indices: [139]

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
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (evaluating properties)?
            3. Is it a compositional question (combining facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Parallel analysis of documents
        document_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document:
                - Extract key entities and relationships
                - Identify potential bridge entities
                - Summarize relevant facts""",
                context=document
            ) for document in self.extract_documents()]
        )

        # Step 3: Identify bridge entities
        bridge_entities = await self.ensemble(
            instruction="""Identify bridge entities that connect the documents:
            - Select entities mentioned across multiple documents
            - Prioritize entities relevant to the question""",
            contexts_list=document_summaries
        )

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities:
            {bridge_entities}
            
            Construct a reasoning chain that answers the question:
            - Link entities across documents
            - Ensure logical coherence
            - Validate each step with evidence from the documents""",
            context=question_type
        )

        # Step 5: Extract and validate the answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning chain:
            {reasoning_chain}
            
            Ensure the answer is:
            - Factually correct
            - Directly supported by evidence
            - In the required format (short text span or yes/no)""",
            context=reasoning_chain
        )

        return answer

    def extract_documents(self):
        """Helper function to extract individual documents from the problem text."""
        # Placeholder implementation: Assumes documents are separated by titles
        sections = self.problem_text.split("**Document")
        return [section.strip() for section in sections if section.strip()]