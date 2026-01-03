# Workflow ID: hotpotqa_271_0
# Benchmark: hotpotqa
# Data Indices: [355]

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

        # Step 1: Classify question type and extract key entities/relationships
        analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (evaluating properties)?
            3. Is it a compositional question (combining facts)?
            Additionally, extract all named entities and relationships from the context documents.
            Format the output as:
            - Question Type: [type]
            - Entities: [list of entities]
            - Relationships: [list of relationships]""",
            context=""
        )

        # Step 2: Parallel exploration of reasoning paths
        question_type = "bridge" if "bridge" in analysis.lower() else "comparison" if "comparison" in analysis.lower() else "compositional"
        entities = [line.split(":")[1].strip() for line in analysis.split("\n") if "Entities" in line][0].split(", ")
        relationships = [line.split(":")[1].strip() for line in analysis.split("\n") if "Relationships" in line][0].split(", ")

        reasoning_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"""Explore reasoning path for entity: {entity}
                - Identify related documents
                - Extract relevant facts
                - Build reasoning chain""",
                context=analysis
            ) for entity in entities]
        )

        # Step 3: Synthesize reasoning chains
        reasoning_chain = await self.ensemble(
            instruction="""Evaluate the reasoning paths and select the most coherent chain:
            - Ensure logical consistency
            - Prioritize chains supported by multiple documents
            - Resolve ambiguities using context""",
            contexts_list=reasoning_paths
        )

        # Step 4: Extract and refine answer
        extracted_answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Identify the exact text span that answers the question
            - Ensure factual correctness
            Reasoning Chain: {reasoning_chain}""",
            context=""
        )

        refined_answer = await self.revise(
            instruction="""Refine the extracted answer:
            - Ensure it matches the required format (short text span or yes/no)
            - Validate against supporting facts
            - Improve clarity and precision""",
            context=extracted_answer
        )

        return refined_answer