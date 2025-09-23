# Workflow ID: hotpotqa_132_0
# Benchmark: hotpotqa
# Data Indices: [62]

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

        # Initial analysis: classify question type and extract key entities
        classification = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining multiple facts)?
            Provide detailed reasoning for your classification.""",
            context=""
        )

        # Extract potential bridge entities and facts in parallel
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, numbers, and relationships from Document {i+1}.
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Identify bridge entities that connect documents
        bridge_entities = await self.ensemble(
            instruction="""Identify bridge entities that connect documents:
            - Shared entities (people, places, terms)
            - Relationships between entities
            Select the most relevant connections.""",
            contexts_list=extracted_entities
        )

        # Build reasoning chains by linking facts through bridge entities
        reasoning_chains = []
        for entity in bridge_entities.split("\n"):
            chain = await self.generate(
                instruction=f"""Using the bridge entity '{entity}', build a reasoning chain:
                - Trace how this entity connects documents
                - Extract relevant facts from each document
                - Formulate a coherent chain leading to the answer.""",
                context=bridge_entities
            )
            reasoning_chains.append(chain)

        # Validate and refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and improve this reasoning chain:
                - Check factual accuracy
                - Ensure logical consistency
                - Clarify ambiguous steps""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Extract the precise answer from the final document in the chain
        answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer from this reasoning chain:
                - Identify the final fact or conclusion
                - Ensure it directly answers the question""",
                context=chain
            ) for chain in refined_chains]
        )

        # Ensemble to select the best answer
        final_answer = await self.ensemble(
            instruction="""Select the best answer:
            - Most factually accurate
            - Best supported by evidence
            - Most concise and clear""",
            contexts_list=answers
        )

        return final_answer