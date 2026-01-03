# Workflow ID: hotpotqa_265_0
# Benchmark: hotpotqa
# Data Indices: [332, 27]

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

        # Step 1: Initial Analysis - Classify problem and extract key components
        analysis = await self.generate(
            instruction="""Classify the problem type (bridge, comparison, compositional).
            Extract key entities, relationships, and constraints from the question.
            Provide structured output including:
            - Problem type
            - Key entities
            - Relationships between entities
            - Constraints or conditions""",
            context=""
        )

        # Step 2: Entity and Relationship Extraction
        entities = await self.generate(
            instruction=f"""Extract named entities and their relationships from the context documents.
            Focus on entities related to: {analysis}.
            Format as structured list with categories:
            - Entities: [names and roles]
            - Relationships: [connections between entities]""",
            context=""
        )

        # Step 3: Parallel Exploration - Identify potential bridge entities
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Identify bridge entities connecting documents based on: {entities}.
                Focus on entities mentioned in multiple documents.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Identify alternative relationships or indirect connections based on: {entities}.
                Consider less obvious links that might still be relevant.""",
                context=entities
            )
        )

        # Step 4: Reasoning Chain Construction
        reasoning_chain = await self.revise(
            instruction=f"""Construct a reasoning chain connecting the documents using: {candidates}.
            Ensure the chain is logical and factually supported by the context documents.""",
            context="\n".join(candidates)
        )

        # Step 5: Answer Extraction
        answer_candidates = await asyncio.gather(
            self.summarize(
                instruction=f"""Extract the precise answer from the reasoning chain: {reasoning_chain}.
                Ensure the answer is factual and supported by the context documents.""",
                context=reasoning_chain
            ),
            self.summarize(
                instruction=f"""Extract an alternative answer considering indirect connections: {reasoning_chain}.
                Ensure the answer is factual and supported by the context documents.""",
                context=reasoning_chain
            )
        )

        # Step 6: Ensemble for Validation
        final_answer = await self.ensemble(
            instruction="""Select the most accurate and complete answer from the candidates.
            Ensure the selected answer is factually correct and directly supported by the context documents.""",
            contexts_list=answer_candidates
        )

        return final_answer