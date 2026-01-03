# Workflow ID: hotpotqa_40_0
# Benchmark: hotpotqa
# Data Indices: [438, 28]

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
            instruction="""Analyze the question and context documents:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities mentioned in the question.
            3. Identify potential bridge entities that connect documents.
            4. Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Exploration of Documents
        # Extract key entities and bridge entities from initial analysis
        entities = await self.generate(
            instruction="Extract all named entities, bridge entities, and relationships from the analysis.",
            context=initial_analysis
        )
        
        # Explore relevant documents in parallel
        document_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            document_tasks.append(
                self.generate(
                    instruction=f"""Explore Document {i}:
                    1. Identify mentions of key entities: {entities}.
                    2. Extract relevant facts or properties.
                    3. Determine how these facts relate to the question.""",
                    context=""
                )
            )
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Build Reasoning Chains
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from all documents:
            1. Identify bridge entities that connect documents.
            2. Follow the chain of reasoning to derive intermediate conclusions.
            3. Resolve conflicts or ambiguities.""",
            contexts_list=document_results
        )

        # Step 4: Answer Extraction and Validation
        extracted_answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            1. Identify the exact answer span in the text.
            2. Ensure the answer is factually correct based on supporting facts.
            3. Format the answer as a short text span or yes/no response.
            Reasoning Chain: {reasoning_chain}""",
            context=""
        )

        # Step 5: Refine and Validate the Answer
        final_answer = await self.revise(
            instruction="Refine the extracted answer for clarity and precision.",
            context=extracted_answer
        )

        return final_answer