# Workflow ID: hotpotqa_244_0
# Benchmark: hotpotqa
# Data Indices: [424]

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
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (analyzing properties across documents)?
            3. Is it a compositional question (combining multiple facts)?
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, relationships, and key facts from the documents:
            - Entities: Names, organizations, locations, etc.
            - Relationships: Connections between entities
            - Key facts: Important statements or numerical values""",
            context=""
        )

        # Step 3: Identify bridge entities or properties (parallel fork)
        if "bridge" in question_type.lower():
            bridge_perspectives = await asyncio.gather(
                self.generate(instruction="Identify shared entities connecting documents...", context=entities),
                self.generate(instruction="Find implicit connections between entities...", context=entities)
            )
            bridge_entities = await self.ensemble(
                instruction="Synthesize perspectives to identify the most likely bridge entities...",
                contexts_list=bridge_perspectives
            )
        elif "comparison" in question_type.lower():
            property_perspectives = await asyncio.gather(
                self.generate(instruction="Compare properties across documents...", context=entities),
                self.generate(instruction="Analyze numerical or categorical differences...", context=entities)
            )
            bridge_entities = await self.ensemble(
                instruction="Synthesize perspectives to identify the most relevant properties...",
                contexts_list=property_perspectives
            )
        else:
            bridge_entities = await self.generate(
                instruction="Combine multiple facts to derive the reasoning chain...",
                context=entities
            )

        # Step 4: Build reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified entities/properties: {bridge_entities}
            Construct a logical reasoning chain that connects the documents:
            - Start with the initial entity/property
            - Trace the connections across documents
            - End with the final entity/property leading to the answer""",
            context=entities
        )

        # Step 5: Extract and refine the answer
        raw_answer = await self.generate(
            instruction=f"""Based on the reasoning chain: {reasoning_chain}
            Extract the precise answer span from the documents:
            - Ensure it is a short text span or yes/no response
            - Match the expected answer format""",
            context=""
        )
        refined_answer = await self.revise(
            instruction="Refine the extracted answer for clarity and precision...",
            context=raw_answer
        )

        return refined_answer