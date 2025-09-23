# Workflow ID: hotpotqa_77_0
# Benchmark: hotpotqa
# Data Indices: [215, 94]

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
            instruction="""Analyze the problem:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities, relationships, and constraints.
            3. Highlight potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Analyze documents in parallel
        documents = re.findall(r"Document \d+: (.+?)\n", self.problem_text)
        parallel_tasks = [
            self.generate(
                instruction=f"""Analyze this document:
                1. Extract all entities and relationships.
                2. Identify connections to bridge entities from initial analysis.
                Document Content: {doc}""",
                context=initial_analysis
            ) for doc in documents
        ]
        document_analyses = await asyncio.gather(*parallel_tasks)

        # Step 3: Reasoning Chain Construction - Build a logical path across documents
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain:
            1. Use insights from document analyses: {document_analyses}.
            2. Connect documents through shared entities or relationships.
            3. Ensure the chain leads to the final answer.
            Provide detailed reasoning steps.""",
            context=initial_analysis
        )

        # Step 4: Validation and Refinement - Validate the reasoning chain
        validation = await self.revise(
            instruction=f"""Validate the reasoning chain:
            1. Check factual accuracy against provided documents.
            2. Address any gaps or ambiguities.
            Reasoning Chain: {reasoning_chain}""",
            context=document_analyses[0]  # Use one analysis as a starting point
        )

        # Step 5: Final Answer Extraction - Extract the precise answer span
        final_answer = await self.summarize(
            instruction=f"""Extract the final answer:
            1. Use the validated reasoning chain: {validation}.
            2. Identify the exact answer span from the documents.
            3. Ensure the answer is concise and factual.""",
            context=validation
        )

        return final_answer