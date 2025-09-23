# Workflow ID: hotpotqa_129_0
# Benchmark: hotpotqa
# Data Indices: [199]

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
            - Bridge: Requires connecting documents through shared entities.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive the answer.
            Provide the classification along with reasoning.""",
            context=""
        )

        # Step 2: Extract entities and facts from documents
        entities_and_facts = await self.generate(
            instruction=f"""Extract all named entities, relationships, and relevant facts from the documents.
            Focus on information relevant to the question type: {question_type}.
            Format as a structured list with categories:
            - Entities: [names and roles]
            - Relationships: [connections between entities]
            - Facts: [key information related to entities]""",
            context=""
        )

        # Step 3: Identify bridge entities
        bridge_entities = await self.generate(
            instruction=f"""Identify potential bridge entities that connect multiple documents.
            Use the extracted entities and facts: {entities_and_facts}.
            Prioritize entities mentioned in the question and shared across documents.""",
            context=entities_and_facts
        )
        best_bridge_entity = await self.ensemble(
            instruction="Select the most relevant bridge entity based on frequency and relevance.",
            contexts_list=bridge_entities.split("\n")
        )

        # Step 4: Construct the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the bridge entity: {best_bridge_entity}, construct a reasoning chain:
            - Trace the entity's role in each document.
            - Connect the facts to form a logical sequence.
            - Ensure consistency and factual accuracy.""",
            context=entities_and_facts
        )

        # Step 5: Validate and refine the reasoning chain
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain: {reasoning_chain}.
            Check for consistency, factual accuracy, and completeness.
            Identify any gaps or errors.""",
            context=reasoning_chain
        )
        if "error" in validation.lower() or "gap" in validation.lower():
            refined_chain = await self.revise(
                instruction=f"""Refine the reasoning chain to address issues: {validation}.
                Add missing details or correct errors.""",
                context=reasoning_chain
            )
            reasoning_chain = refined_chain

        # Step 6: Extract the precise answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning chain: {reasoning_chain}.
            Ensure the answer is factually correct and matches the required format.""",
            context=reasoning_chain
        )

        return answer