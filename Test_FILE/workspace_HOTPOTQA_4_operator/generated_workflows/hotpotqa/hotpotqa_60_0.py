# Workflow ID: hotpotqa_60_0
# Benchmark: hotpotqa
# Data Indices: [167]

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

        # Step 1: Classify the problem type
        problem_type = await self.generate(
            instruction="""Classify the problem into one of the following types:
            - Bridge Question: Connects information through shared entities.
            - Comparison Question: Compares attributes across documents.
            - Compositional Question: Combines multiple facts to derive an answer.
            Provide the classification along with reasoning.""",
            context=""
        )

        # Step 2: Extract entities and facts from documents (parallel processing)
        documents = await self.generate(
            instruction="Extract all named entities, numbers, and relationships from each document.",
            context=""
        )
        entities_list = documents.split("\n\n")  # Assume each document's entities are separated by double newlines

        # Identify bridge entities or shared concepts
        bridge_entities = await asyncio.gather(
            *[self.generate(
                instruction=f"Identify bridge entities or shared concepts in: {entities}",
                context=entities
            ) for entities in entities_list]
        )
        bridge_entities_summary = await self.ensemble(
            instruction="Synthesize bridge entities across documents.",
            contexts_list=bridge_entities
        )

        # Step 3: Build reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities: {bridge_entities_summary}
            Construct a reasoning chain that connects facts across documents to answer the question.
            Ensure the chain is logically consistent and factually supported.""",
            context=problem_type
        )

        # Step 4: Extract and validate the answer
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction=f"Extract the precise answer span from the reasoning chain: {reasoning_chain}",
                context=""
            ),
            self.generate(
                instruction=f"Validate the extracted answer against supporting facts in the documents.",
                context=reasoning_chain
            )
        )
        final_answer = await self.ensemble(
            instruction="Select the most accurate and factually supported answer.",
            contexts_list=answer_candidates
        )

        return final_answer