# Workflow ID: hotpotqa_215_0
# Benchmark: hotpotqa
# Data Indices: [313]

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

        # Step 1: Initial Analysis - Classify question type and identify key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify it as a bridge, comparison, or compositional question.
            2. Identify key entities (e.g., people, places, organizations).
            3. Note any specific constraints or requirements.
            Provide structured output.""",
            context=""
        )

        # Step 2: Document Analysis - Extract relevant facts from each document
        documents = re.findall(r'Document \d+:.*?(?=\n\n|$)', self.problem_text, re.DOTALL)
        document_tasks = [
            self.generate(
                instruction=f"""Extract all relevant facts from this document:
                {doc}
                Focus on entities and facts related to: {initial_analysis}""",
                context=""
            ) for doc in documents
        ]
        extracted_facts = await asyncio.gather(*document_tasks)

        # Step 3: Reasoning Chain Construction - Connect facts across documents
        reasoning_chain = await self.ensemble(
            instruction=f"""Build a reasoning chain using these facts:
            {extracted_facts}
            Follow these steps:
            1. Identify bridge entities that connect documents.
            2. Construct a logical chain linking the entities.
            3. Ensure all steps are factually supported.
            Provide the complete reasoning chain.""",
            contexts_list=extracted_facts
        )

        # Step 4: Answer Extraction - Extract precise answer from the final document
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            Extract the precise answer from the final document.
            Ensure the answer is a short text span or yes/no response.""",
            context=reasoning_chain
        )

        # Step 5: Validation and Refinement - Validate the reasoning chain and refine the answer
        refined_answer = await self.revise(
            instruction=f"""Validate the reasoning chain and refine the answer:
            Reasoning Chain: {reasoning_chain}
            Extracted Answer: {answer_extraction}
            Ensure the answer is factually correct and matches the question requirements.""",
            context=answer_extraction
        )

        return refined_answer