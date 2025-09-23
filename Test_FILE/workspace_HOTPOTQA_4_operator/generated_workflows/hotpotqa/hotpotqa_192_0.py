# Workflow ID: hotpotqa_192_0
# Benchmark: hotpotqa
# Data Indices: [473, 302]

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

        # Step 1: Analyze the question type and extract key components
        analysis = await self.generate(
            instruction="""Analyze the question and classify it into one of the following types:
            - Bridge Question: Requires connecting documents through shared entities.
            - Comparison Question: Requires comparing properties across documents.
            - Compositional Question: Requires combining multiple facts to derive the answer.
            Also, extract key entities and relationships mentioned in the question.""",
            context=""
        )

        # Step 2: Parallel exploration of entities, relationships, and document relevance
        entities_task = self.generate(
            instruction="Extract all named entities (people, places, organizations, etc.) from the documents.",
            context=analysis
        )
        relationships_task = self.generate(
            instruction="Identify relationships between entities and documents based on shared concepts.",
            context=analysis
        )
        relevance_task = self.generate(
            instruction="Determine which documents are most relevant to answering the question.",
            context=analysis
        )
        entities, relationships, relevance = await asyncio.gather(entities_task, relationships_task, relevance_task)

        # Step 3: Synthesize the reasoning chain
        reasoning_chain = await self.ensemble(
            instruction="""Combine the extracted entities, relationships, and document relevance into a coherent reasoning chain.
            Ensure the chain connects at least two documents and leads logically to the answer.""",
            contexts_list=[entities, relationships, relevance]
        )

        # Step 4: Conditional branching based on question type
        if "bridge" in analysis.lower():
            answer = await self.generate(
                instruction=f"""Using the reasoning chain: {reasoning_chain}
                Identify the bridge entity that connects the documents and extract the precise answer span related to it.""",
                context=reasoning_chain
            )
        elif "comparison" in analysis.lower():
            answer = await self.generate(
                instruction=f"""Using the reasoning chain: {reasoning_chain}
                Compare the relevant properties across documents and determine the correct answer.""",
                context=reasoning_chain
            )
        else:  # Compositional question
            answer = await self.generate(
                instruction=f"""Using the reasoning chain: {reasoning_chain}
                Combine multiple facts sequentially to derive the final answer.""",
                context=reasoning_chain
            )

        # Step 5: Validate and refine the answer
        validation = await self.generate(
            instruction=f"""Validate the answer: {answer}
            Check for factual accuracy, precision, and alignment with the reasoning chain.""",
            context=reasoning_chain
        )
        if "error" in validation.lower() or "incorrect" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Revise the answer based on validation feedback: {validation}
                Ensure the answer is factually correct and precise.""",
                context=answer
            )
            return refined_answer
        else:
            return answer