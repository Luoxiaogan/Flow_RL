# Workflow ID: hotpotqa_62_0
# Benchmark: hotpotqa
# Data Indices: [209, 193]

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

        # Initial analysis to classify question type
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Requires connecting entities across documents.
            2. Comparison Question: Involves comparing properties or facts.
            3. Compositional Question: Needs combining multiple facts to derive an answer.
            Provide a clear classification and brief rationale.""",
            context=""
        )

        # Extract entities and facts from each document
        entities_facts_tasks = [
            self.generate(
                instruction=f"""Extract all relevant entities and facts from Document {i+1}.
                Focus on named entities, relationships, and key statements related to the question.
                Format as structured list with categories:
                - Entities: [names and roles]
                - Facts: [key statements and relationships]""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        entities_facts = await asyncio.gather(*entities_facts_tasks)

        # Identify bridge entities or comparative elements
        connection_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Identify potential bridge entities or comparative elements in Document {i+1} that relate to the question.
                Consider shared entities, overlapping themes, or contrasting properties.
                Provide a list of candidates with brief explanations.""",
                context=ef
            ) for i, ef in enumerate(entities_facts)]
        )

        # Evaluate and select best connections
        best_connections = await self.ensemble(
            instruction="""Evaluate the potential connections across documents.
            Select the most plausible bridge entities or comparative elements based on relevance to the question and coherence across documents.
            Provide a ranked list with explanations.""",
            contexts_list=connection_candidates
        )

        # Construct reasoning chain
        reasoning_chain = await self.revise(
            instruction=f"""Using the selected connections:
            {best_connections}
            
            Construct a coherent reasoning chain that connects the information across documents to answer the question.
            Ensure each step logically follows from the previous and leads to the final answer.
            Highlight any assumptions or missing links.""",
            context=best_connections
        )

        # Extract precise answer
        final_answer = await self.summarize(
            instruction=f"""From the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer to the question.
            Ensure the answer is a short factual span directly from the documents or a yes/no response if applicable.
            Provide the exact answer with minimal context.""",
            context=reasoning_chain
        )

        return final_answer