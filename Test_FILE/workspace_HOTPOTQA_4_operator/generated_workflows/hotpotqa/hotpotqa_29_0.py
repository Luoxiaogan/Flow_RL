# Workflow ID: hotpotqa_29_0
# Benchmark: hotpotqa
# Data Indices: [407, 290]

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
            - Bridge: Requires connecting documents through shared entities (e.g., "What nationality is the director of [movie]?")
            - Comparison: Requires comparing properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional: Requires combining multiple facts to derive the answer (e.g., "Who directed the movie starring actor X who also appeared in movie Y?")
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        entities_extraction_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            entities_extraction_tasks.append(
                self.generate(
                    instruction=f"""Extract all named entities and their relationships from Document {i}.
                    Format as structured list with categories:
                    - People: [names and roles]
                    - Places: [locations and contexts]
                    - Numbers: [values and what they represent]
                    - Actions: [what happens and when]""",
                    context=""
                )
            )
        extracted_entities = await asyncio.gather(*entities_extraction_tasks)

        # Step 3: Build the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {extracted_entities}
            
            Build a reasoning chain to answer the question:
            {question_type}
            
            Connect entities across documents to form a logical path to the answer.
            Highlight the key connections and supporting facts.""",
            context="".join(extracted_entities)
        )

        # Step 4: Validate and refine the reasoning chain
        refined_reasoning = await self.revise(
            instruction=f"""Review the reasoning chain:
            {reasoning_chain}
            
            Ensure it is accurate, complete, and logically consistent.
            Refine any unclear or incorrect parts.""",
            context=reasoning_chain
        )

        # Step 5: Synthesize the answer
        answer = await self.ensemble(
            instruction=f"""Using the refined reasoning chain:
            {refined_reasoning}
            
            Synthesize the final answer in a short text span or yes/no format.
            Include supporting facts from different documents.""",
            contexts_list=[refined_reasoning, *extracted_entities]
        )

        return answer