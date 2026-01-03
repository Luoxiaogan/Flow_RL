# Workflow ID: hotpotqa_91_0
# Benchmark: hotpotqa
# Data Indices: [343]

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
        
        # Phase 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities mentioned in the question.
            3. Determine potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )
        
        # Phase 2: Entity Extraction and Bridging
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_titles = [line.split(":")[0].strip() for line in documents.split("\n") if line.startswith("Document")]
        entity_tasks = [
            self.generate(
                instruction=f"""Extract entities and relationships from {doc}:
                - Identify named entities (people, places, numbers).
                - Highlight connections to other entities/documents.
                - Focus on relevance to the question.""",
                context=analysis
            ) for doc in doc_titles
        ]
        entity_results = await asyncio.gather(*entity_tasks)
        
        bridging_entities = await self.ensemble(
            instruction="Identify bridge entities that connect documents and support the reasoning chain.",
            contexts_list=entity_results
        )
        
        # Phase 3: Reasoning Chain Construction
        reasoning_chain = ""
        for entity in bridging_entities.split("\n"):
            step = await self.generate(
                instruction=f"""Using {entity}, build the next step in the reasoning chain:
                - Find supporting facts in the documents.
                - Connect to the previous step logically.
                - Ensure progress toward answering the question.""",
                context=reasoning_chain
            )
            reasoning_chain += f"\n{step}"
        
        # Phase 4: Answer Extraction and Validation
        answer = await self.summarize(
            instruction="Extract the precise answer from the reasoning chain. Ensure it matches the question format.",
            context=reasoning_chain
        )
        
        validation = await self.generate(
            instruction=f"""Validate the answer:
            - Check consistency with supporting facts.
            - Ensure factual correctness.
            - Flag any ambiguities or uncertainties.""",
            context=answer
        )
        
        # Phase 5: Iterative Refinement
        if "uncertain" in validation.lower() or "ambiguous" in validation.lower():
            refined_answer = await self.revise(
                instruction="Resolve ambiguities and refine the answer based on validation feedback.",
                context=answer
            )
            return refined_answer
        
        return answer