# Workflow ID: hotpotqa_30_0
# Benchmark: hotpotqa
# Data Indices: [303, 276]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction generation is powerful
        """
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Step 1: Initial Analysis - Classify question and extract bridge entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract all named entities and relationships mentioned in the question.
            3. Identify potential bridge entities that connect documents.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Document Scanning - Extract relevant information from documents
        documents = [f"Document {i+1}" for i in range(10)]  # Assuming 10 documents
        document_tasks = [
            self.generate(
                instruction=f"""Scan {doc} for relevant information:
                1. Search for mentions of the bridge entities: {initial_analysis}.
                2. Extract sentences or paragraphs containing these entities.
                3. Include surrounding context for clarity.""",
                context=""
            )
            for doc in documents
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Build Reasoning Chain - Synthesize information across documents
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from the following documents:
            1. Identify logical connections between the extracted facts.
            2. Construct a reasoning chain that leads to the answer.
            3. Resolve any contradictions using evidence from other documents.""",
            contexts_list=document_results
        )

        # Step 4: Answer Extraction - Extract precise answer from reasoning chain
        answer_extraction = await self.summarize(
            instruction="""Extract the final answer:
            1. Identify the exact sentence or phrase that contains the answer.
            2. Validate the answer against the question and supporting facts.
            3. Ensure the answer is precise and verbatim from the text.""",
            context=reasoning_chain
        )

        # Step 5: Refinement - Improve clarity and precision
        refined_answer = await self.revise(
            instruction="""Refine the extracted answer:
            1. Verify factual accuracy.
            2. Improve clarity and conciseness.
            3. Ensure the answer matches the expected format.""",
            context=answer_extraction
        )

        return refined_answer