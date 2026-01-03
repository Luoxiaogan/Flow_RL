# Workflow ID: hotpotqa_168_0
# Benchmark: hotpotqa
# Data Indices: [132, 253]

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

        # Step 1: Initial Analysis - Classify problem and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the type of question (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Determine what information is needed to answer the question.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Document Processing - Identify bridge entities and extract facts
        documents = re.findall(r"Document \d+:.*?(?=\n\nDocument|\n\n\*\*QUESTION)", self.problem_text, re.DOTALL)
        document_tasks = [
            self.generate(
                instruction=f"""Analyze this document:
                1. Identify entities related to the problem.
                2. Extract relevant facts and relationships.
                3. Highlight potential bridge entities.
                Document content: {doc}""",
                context=initial_analysis
            ) for doc in documents
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Synthesize Information - Construct reasoning chain
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from all documents:
            1. Connect bridge entities across documents.
            2. Build a reasoning chain to answer the question.
            3. Ensure the chain is logically consistent and factually supported.""",
            contexts_list=document_results
        )

        # Step 4: Answer Extraction and Validation
        refined_answer = await self.revise(
            instruction="""Extract the precise answer from the reasoning chain:
            1. Ensure the answer is factually correct.
            2. Validate against the original documents.
            3. Format the answer as a short text span or yes/no response.""",
            context=reasoning_chain
        )

        # Step 5: Final Output
        return refined_answer