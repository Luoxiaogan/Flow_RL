# Workflow ID: hotpotqa_314_0
# Benchmark: hotpotqa
# Data Indices: [426, 232]

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
            - Comparison: Requires comparing properties across documents.
            - Compositional: Requires combining multiple facts to derive the answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        entities_tasks = []
        for i in range(10):  # Assuming up to 10 documents
            entities_tasks.append(
                self.generate(
                    instruction=f"""Extract all named entities, relationships, and key facts from Document {i+1}.
                    Format as structured list with categories:
                    - Entities: [names and roles]
                    - Relationships: [connections between entities]
                    - Key Facts: [important details]""",
                    context=""
                )
            )
        entities_results = await asyncio.gather(*entities_tasks)

        # Step 3: Identify bridge entities (if applicable)
        if "Bridge" in question_type:
            bridge_entity = await self.ensemble(
                instruction="Identify the most relevant bridge entity connecting the documents.",
                contexts_list=entities_results
            )
        else:
            bridge_entity = ""

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified entities and relationships:
            {bridge_entity}
            Construct a reasoning chain that connects the documents to answer the question.
            Ensure the chain is logically sound and supported by evidence.""",
            context="\n".join(entities_results)
        )

        # Step 5: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            {reasoning_chain}
            Ensure the answer is factually correct and matches the required format.""",
            context=""
        )

        # Optional: Revise answer for clarity and correctness
        final_answer = await self.revise(
            instruction="Ensure the answer is precise, factual, and matches the required format.",
            context=answer
        )

        return final_answer