# Workflow ID: hotpotqa_306_0
# Benchmark: hotpotqa
# Data Indices: [174]

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

        # Step 1: Classify the question type and identify key entities
        classification = await self.generate(
            instruction="""Classify the question type:
            - Is it a bridge question, comparison question, or compositional question?
            - Identify key entities and relationships.
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Extract named entities and relationships from documents
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities and relationships from Document {i+1}:
                - People, places, organizations, dates, etc.
                - Relationships between entities
                - Highlight potential bridge entities.""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Identify the most relevant bridge entities
        bridge_entities = await self.ensemble(
            instruction="""Identify the most relevant bridge entities:
            - Entities that connect multiple documents
            - Entities mentioned in the question
            - Entities with strong relationships to the question context.""",
            contexts_list=extracted_entities
        )

        # Step 4: Build reasoning chains across documents
        reasoning_chains = []
        for entity in re.findall(r'\b\w+\b', bridge_entities):
            chain = await self.generate(
                instruction=f"""Build a reasoning chain for the entity '{entity}':
                - Trace its appearance across documents
                - Identify supporting facts
                - Ensure logical consistency.""",
                context=classification
            )
            reasoning_chains.append(chain)

        # Step 5: Refine and validate the reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the reasoning chain for accuracy:
                - Validate facts against documents
                - Resolve ambiguities
                - Ensure logical flow.""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 6: Extract the precise answer
        condensed_answers = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Condense the reasoning chain into a concise answer:
                - Extract the exact text span or yes/no response
                - Match the required answer format.""",
                context=chain
            ) for chain in refined_chains]
        )

        # Step 7: Select the best answer
        final_answer = await self.ensemble(
            instruction="""Select the best answer:
            - Factually correct
            - Matches the question format
            - Supported by strongest evidence.""",
            contexts_list=condensed_answers
        )

        return final_answer