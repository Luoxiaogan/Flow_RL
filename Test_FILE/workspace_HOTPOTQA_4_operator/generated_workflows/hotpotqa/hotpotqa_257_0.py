# Workflow ID: hotpotqa_257_0
# Benchmark: hotpotqa
# Data Indices: [359]

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

        # Step 1: Classify the question type and extract key entities
        classification = await self.generate(
            instruction="""Classify the question type and extract key entities:
            1. Is this a bridge, comparison, or compositional question?
            2. Identify all named entities (people, places, organizations).
            3. Highlight potential bridge entities that connect documents.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Analyze documents in parallel to find supporting facts
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        document_tasks = []
        for doc in documents[1:]:  # Skip the first empty split
            task = self.generate(
                instruction=f"""Analyze this document for relevant information:
                - Focus on entities and relationships mentioned in the classification.
                - Extract facts that support answering the question.
                Document content: {doc}""",
                context=classification
            )
            document_tasks.append(task)
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Summarize findings from each document
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the analysis into key facts supporting the reasoning chain.",
                context=result
            ) for result in document_results]
        )

        # Step 4: Synthesize findings into a unified reasoning chain
        synthesis = await self.ensemble(
            instruction="""Synthesize the summaries into a unified reasoning chain:
            - Identify the bridge entity connecting documents.
            - Follow the reasoning chain to derive the answer.
            - Ensure the final answer is supported by evidence from multiple documents.""",
            contexts_list=summaries
        )

        # Step 5: Refine the synthesized reasoning chain
        refined_answer = await self.revise(
            instruction="""Refine the synthesized reasoning chain:
            - Ensure clarity and precision in the final answer.
            - Verify that the answer matches the expected format (short text span or yes/no).
            - Resolve any ambiguities or contradictions.""",
            context=synthesis
        )

        return refined_answer