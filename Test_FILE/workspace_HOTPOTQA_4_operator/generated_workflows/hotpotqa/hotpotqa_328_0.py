# Workflow ID: hotpotqa_328_0
# Benchmark: hotpotqa
# Data Indices: [421]

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
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge Question: Requires connecting entities across documents.
            - Comparison Question: Requires comparing properties across documents.
            - Compositional Question: Requires combining multiple facts.
            Provide the classification along with reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        entities = await self.generate(
            instruction=f"""Extract all named entities and their relationships from the provided documents.
            Focus on entities relevant to the question type: {classification}.
            Format as structured list with categories:
            - People: [names and roles]
            - Organizations: [bands, companies, etc.]
            - Dates: [founding years, release dates, etc.]
            - Relationships: [membership, founding, collaboration, etc.]""",
            context=""
        )

        # Step 3: Identify cross-document connections
        connections = await self.ensemble(
            instruction=f"""Identify connections between documents based on shared entities.
            Use the extracted entities and relationships: {entities}.
            Highlight bridge entities that connect multiple documents.""",
            contexts_list=[entities] * len(self.problem_text.split("Document"))
        )

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain to answer the question.
            Use the identified connections: {connections}.
            Follow these guidelines based on the question type: {classification}.
            - Bridge Question: Trace relationships step-by-step.
            - Comparison Question: Aggregate counts or properties.
            - Compositional Question: Combine multiple facts logically.""",
            context=connections
        )

        # Step 5: Refine and validate the reasoning chain
        refined_chain = await self.revise(
            instruction=f"""Refine the reasoning chain for clarity and logical consistency.
            Ensure all steps are factually correct and supported by the documents.
            Address any ambiguities or missing links.""",
            context=reasoning_chain
        )

        # Step 6: Extract and summarize the final answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the refined reasoning chain: {refined_chain}.
            Format as a short text span or yes/no response.
            Include supporting facts from the documents.""",
            context=refined_chain
        )

        return answer