# Workflow ID: hotpotqa_223_0
# Benchmark: hotpotqa
# Data Indices: [413, 388]

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
            instruction="""Classify the question into one of the following types:
            1. Bridge: Requires connecting entities across documents.
            2. Comparison: Requires comparing properties across documents.
            3. Compositional: Requires combining multiple facts.
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Identify bridge entities
        bridge_entities = await self.generate(
            instruction=f"""Based on the question type: {question_type}
            Extract all named entities, relationships, and key terms from the question and documents.
            Focus on entities that connect documents.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 3: Analyze documents in parallel
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for information related to the bridge entities: {bridge_entities}
                Identify relevant sentences and their relationships.
                Format as structured findings.""",
                context=document
            ) for document in self.problem_text.split('Document ')[1:]]
        )

        # Step 4: Synthesize reasoning chain
        reasoning_chain = await self.ensemble(
            instruction=f"""Synthesize the reasoning chain by connecting the bridge entities: {bridge_entities}
            Use the document analyses: {document_analyses}
            Follow the logical chain to arrive at the final document containing the answer.""",
            contexts_list=document_analyses
        )

        # Step 5: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain: {reasoning_chain}
            Ensure the answer is a short text span or a yes/no response.
            Validate the answer against all relevant documents.""",
            context=reasoning_chain
        )

        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer: {answer}
            Cross-check with all relevant documents to ensure factual correctness.
            Resolve any ambiguities or contradictions.""",
            context=answer
        )

        return validated_answer