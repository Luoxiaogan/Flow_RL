# Workflow ID: hotpotqa_162_0
# Benchmark: hotpotqa
# Data Indices: [201, 433]

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
            1. Bridge Question: Requires connecting entities across documents.
            2. Comparison Question: Involves contrasting properties or attributes.
            3. Compositional Question: Needs combining multiple facts.
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        async def extract_entities(doc):
            return await self.generate(
                instruction=f"""Extract all named entities and relationships from the document:
                Document: {doc}
                Format as structured list with categories:
                - People: [names and roles]
                - Organizations: [names and descriptions]
                - Locations: [names and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )

        documents = [doc.split("\n", 1)[1] for doc in self.problem_text.split("**Document ")[1:]]
        entities_list = await asyncio.gather(*[extract_entities(doc) for doc in documents])

        # Step 3: Identify bridge entities or relevant facts
        if "bridge" in question_type.lower():
            bridge_entities = await self.ensemble(
                instruction="Identify shared entities that appear in multiple documents.",
                contexts_list=entities_list
            )
        else:
            bridge_entities = ""

        # Step 4: Construct the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified entities and relationships:
            Entities: {bridge_entities}
            Documents: {documents}
            
            Construct a reasoning chain that connects the facts to answer the question.
            Provide explicit references to sentences in the documents.""",
            context=""
        )

        # Step 5: Extract the final answer
        answer = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the documents.
            Ensure the answer is factually correct and directly addresses the question.""",
            context=""
        )

        # Step 6: Validate and refine the answer
        validated_answer = await self.revise(
            instruction="Validate the answer against the supporting facts and refine if necessary.",
            context=answer
        )

        return validated_answer