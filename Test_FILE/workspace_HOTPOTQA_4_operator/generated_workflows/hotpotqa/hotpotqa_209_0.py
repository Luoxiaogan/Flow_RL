# Workflow ID: hotpotqa_209_0
# Benchmark: hotpotqa
# Data Indices: [291]

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
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting information through shared entities.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive an answer.
            Provide the classification and explain your reasoning.""",
            context=""
        )

        # Step 2: Extract entities and facts from documents
        documents = await self.generate(
            instruction="Identify all documents provided in the context.",
            context=""
        )
        document_tasks = []
        for doc in documents.split("\n"):
            task = self.generate(
                instruction=f"""Extract entities and relevant facts from the following document:
                {doc}
                Focus on entities that could serve as bridge connections.""",
                context=""
            )
            document_tasks.append(task)
        extracted_facts = await asyncio.gather(*document_tasks)

        # Step 3: Build the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted facts:
            {extracted_facts}
            
            Construct a reasoning chain that connects the information across documents.
            Follow the chain to arrive at the final answer.""",
            context=""
        )

        # Step 4: Extract the final answer
        final_answer = await self.summarize(
            instruction=f"""Condense the reasoning chain into a concise answer:
            {reasoning_chain}
            
            Ensure the answer is factually correct and formatted as a short text span.""",
            context=reasoning_chain
        )

        return final_answer