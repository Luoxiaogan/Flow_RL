# Workflow ID: hotpotqa_163_0
# Benchmark: hotpotqa
# Data Indices: [181, 324]

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
            instruction="""Classify the question type:
            - Is it a bridge question (connecting documents via shared entities)?
            - Is it a comparison question (comparing properties across documents)?
            - Is it a compositional question (chaining multiple facts)?
            Provide detailed reasoning for the classification.""",
            context=""
        )

        # Step 2: Extract entities from all documents
        async def extract_entities(doc):
            return await self.generate(
                instruction=f"""Extract named entities from the document:
                - People, organizations, dates, and other key terms
                - Highlight entities mentioned in the question""",
                context=doc
            )

        # Extract entities in parallel
        entity_tasks = [extract_entities(doc) for doc in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document")[1:]]
        entities_list = await asyncio.gather(*entity_tasks)

        # Step 3: Identify bridge entities
        bridge_entities = await self.ensemble(
            instruction="""Identify entities shared across multiple documents:
            - Prioritize entities mentioned in the question
            - Resolve ambiguities using context""",
            contexts_list=entities_list
        )

        # Step 4: Build reasoning chains
        reasoning_chain = await self.generate(
            instruction=f"""Using the bridge entities: {bridge_entities}
            Construct a reasoning chain to connect the question to the answer:
            - For bridge questions, link documents via shared entities
            - For comparison questions, compare properties across documents
            - For compositional questions, chain multiple facts together""",
            context=question_analysis
        )

        # Step 5: Extract the precise answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Ensure the answer is factually correct
            - Match the required format (short text span or yes/no response)""",
            context=reasoning_chain
        )

        # Step 6: Validate and refine the answer
        validated_answer = await self.revise(
            instruction="""Validate the answer against the question:
            - Check for factual accuracy
            - Resolve any ambiguities or conflicts
            - Refine the answer if necessary""",
            context=answer_extraction
        )

        return validated_answer