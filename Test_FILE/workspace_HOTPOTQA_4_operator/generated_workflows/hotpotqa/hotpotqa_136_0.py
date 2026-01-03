# Workflow ID: hotpotqa_136_0
# Benchmark: hotpotqa
# Data Indices: [478]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem to determine its type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Identify all named entities, relationships, and relevant keywords.
            - Provide structured classification and entity list.""",
            context=""
        )

        # Step 2: Parallel Exploration - Identify bridge entities or extract properties
        if "bridge" in initial_analysis.lower():
            # Parallel identification of bridge entities
            bridge_entities = await asyncio.gather(
                self.generate(
                    instruction="Identify shared entities between Document 1 and other documents.",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Identify shared entities between Document 2 and other documents.",
                    context=initial_analysis
                )
            )
            bridge_entities_summary = await self.summarize(
                instruction="Condense the identified bridge entities into a concise list.",
                context="\n".join(bridge_entities)
            )
            reasoning_chain = await self.generate(
                instruction=f"""Using the bridge entities: {bridge_entities_summary}
                Construct a reasoning chain that connects the documents to answer the question.""",
                context=initial_analysis
            )
        else:
            # Parallel extraction of properties for comparison/compositional questions
            property_extractions = await asyncio.gather(
                self.generate(
                    instruction="Extract relevant properties from Document 1.",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Extract relevant properties from Document 2.",
                    context=initial_analysis
                )
            )
            properties_summary = await self.summarize(
                instruction="Summarize the extracted properties for comparison.",
                context="\n".join(property_extractions)
            )
            reasoning_chain = await self.generate(
                instruction=f"""Using the properties: {properties_summary}
                Construct a reasoning chain that compares or combines the information to answer the question.""",
                context=initial_analysis
            )

        # Step 3: Answer Extraction and Validation
        raw_answer = await self.generate(
            instruction=f"""From the reasoning chain: {reasoning_chain}
            Extract the precise answer span that directly answers the question.""",
            context=initial_analysis
        )
        refined_answer = await self.revise(
            instruction="Ensure the answer is factually correct, precise, and matches the expected format.",
            context=raw_answer
        )

        return refined_answer