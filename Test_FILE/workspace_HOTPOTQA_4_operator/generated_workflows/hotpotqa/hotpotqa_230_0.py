# Workflow ID: hotpotqa_230_0
# Benchmark: hotpotqa
# Data Indices: [55]

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
        question_type = await self.generate(
            instruction="""Classify the question type:
            - Bridge: Requires connecting documents through shared entities
            - Comparison: Requires contrasting properties across documents
            - Compositional: Requires combining multiple facts
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract named entities and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, relationships, and key facts:
            - Entities: People, places, objects
            - Relationships: Connections between entities
            - Key Facts: Relevant information from each document
            Organize the output by document.""",
            context=""
        )

        # Step 3: Identify bridge entities (parallel processing)
        bridge_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Identify bridge entities relevant to the question:
                Question: {question_type}
                Document Content: {doc}
                Select entities that connect multiple documents.""",
                context=entities
            ) for doc in entities.split('\n\n')]
        )
        bridge_entities = await self.ensemble(
            instruction="Select the most relevant bridge entities.",
            contexts_list=bridge_candidates
        )

        # Step 4: Construct reasoning chain (conditional branching)
        if "bridge" in question_type.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Construct a reasoning chain using bridge entities:
                Bridge Entities: {bridge_entities}
                Connect facts from different documents to form a coherent chain.""",
                context=entities
            )
        elif "comparison" in question_type.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Compare properties across documents:
                Bridge Entities: {bridge_entities}
                Highlight differences and similarities to answer the question.""",
                context=entities
            )
        else:
            reasoning_chain = await self.generate(
                instruction=f"""Combine multiple facts to derive the answer:
                Bridge Entities: {bridge_entities}
                Synthesize information from different documents.""",
                context=entities
            )

        # Step 5: Extract precise answer
        answer = await self.generate(
            instruction=f"""Extract the exact answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer is a short text span or yes/no response.""",
            context=reasoning_chain
        )

        # Step 6: Validate and refine the answer
        validation = await self.generate(
            instruction=f"""Validate the answer:
            Answer: {answer}
            Reasoning Chain: {reasoning_chain}
            Check for factual accuracy and consistency.""",
            context=reasoning_chain
        )
        if "error" in validation.lower() or "inconsistent" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback:
                Feedback: {validation}
                Original Answer: {answer}""",
                context=answer
            )
            return refined_answer
        else:
            return answer