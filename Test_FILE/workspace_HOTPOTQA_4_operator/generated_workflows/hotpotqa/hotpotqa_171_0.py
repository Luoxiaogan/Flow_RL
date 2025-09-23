# Workflow ID: hotpotqa_171_0
# Benchmark: hotpotqa
# Data Indices: [287]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.llm)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge Question: Connects documents through shared entities.
            - Comparison Question: Compares properties across documents.
            - Compositional Question: Combines multiple facts to derive the answer.
            Provide a clear classification with reasoning.""",
            context=""
        )

        # Step 2: Identify bridge entities and supporting facts (parallel processing)
        documents = await self.generate(
            instruction="Extract all named entities and relationships from the documents. Focus on entities that appear in multiple documents as potential bridge entities.",
            context=""
        )
        parallel_tasks = [
            self.generate(
                instruction=f"Analyze this document for bridge entities and supporting facts: {doc}",
                context=documents
            ) for doc in ["Document 1", "Document 2", "Document 3", "Document 4", "Document 5"]
        ]
        analyses = await asyncio.gather(*parallel_tasks)

        # Step 3: Construct the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities and supporting facts:
            {analyses}
            
            Construct a reasoning chain that connects the documents to answer the question. Ensure the chain is explicit and traceable.""",
            context=question_type
        )
        refined_chain = await self.revise(
            instruction="Refine the reasoning chain to ensure completeness and accuracy. Add missing details and clarify connections.",
            context=reasoning_chain
        )

        # Step 4: Extract the final answer
        final_answer = await self.generate(
            instruction=f"""Using the refined reasoning chain:
            {refined_chain}
            
            Extract the final answer as a short text span from the relevant document. Ensure the answer is precise and verbatim.""",
            context=""
        )

        # Step 5: Validate and finalize the answer
        validation = await self.ensemble(
            instruction="Validate the final answer against the original question and the reasoning chain. Select the most accurate and factually correct answer.",
            contexts_list=[final_answer, reasoning_chain]
        )

        return validation