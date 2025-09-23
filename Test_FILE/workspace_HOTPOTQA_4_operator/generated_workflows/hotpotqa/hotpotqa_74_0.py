# Workflow ID: hotpotqa_74_0
# Benchmark: hotpotqa
# Data Indices: [43, 185]

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
            instruction="""Classify the question into one of the following types:
            - Bridge Question: Requires connecting information through shared entities.
            - Comparison Question: Involves comparing properties (e.g., dates, rankings).
            - Compositional Question: Combines multiple facts to derive the answer.
            Provide a clear classification along with reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities, relationships, and key facts from the documents.
            Format as a structured list:
            - Entities: [names, titles, organizations]
            - Relationships: [how entities are connected]
            - Key Facts: [important sentences or phrases]""",
            context=question_type
        )

        # Step 3: Identify bridge entities (parallel exploration)
        bridge_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Evaluate if {entity} serves as a bridge entity connecting documents.
                - How does it relate to the question?
                - Which documents does it connect?""",
                context=entities
            ) for entity in entities.split("\n") if "entity" in entity.lower()]
        )
        best_bridge = await self.ensemble(
            instruction="Select the most relevant bridge entity based on connection strength and relevance to the question.",
            contexts_list=bridge_candidates
        )

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the bridge entity '{best_bridge}', construct a reasoning chain:
            - Start with the initial document and entity.
            - Follow connections to subsequent documents.
            - End with the document containing the answer.""",
            context=entities
        )

        # Step 5: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the final document in the reasoning chain.
            Ensure it matches the expected format and is factually correct.""",
            context=reasoning_chain
        )

        # Step 6: Iterative refinement (if needed)
        validation = await self.generate(
            instruction=f"""Validate the extracted answer '{answer}' against the context.
            - Is it consistent with the reasoning chain?
            - Does it match the expected format?""",
            context=reasoning_chain
        )
        if "error" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Revise the answer to address issues: {validation}.
                Ensure factual accuracy and precision.""",
                context=answer
            )
            return refined_answer
        
        return answer