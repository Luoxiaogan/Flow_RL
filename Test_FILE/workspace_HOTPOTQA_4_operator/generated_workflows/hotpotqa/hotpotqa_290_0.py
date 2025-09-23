# Workflow ID: hotpotqa_290_0
# Benchmark: hotpotqa
# Data Indices: [127, 173]

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
            - Bridge Question: Requires connecting documents through shared entities.
            - Comparison Question: Requires comparing properties across documents.
            - Compositional Question: Requires combining multiple facts to derive the answer.
            Provide a clear classification with reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        entities_and_relationships = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract entities and relationships from the following document:
                {doc}
                Focus on entities mentioned in the question and their relationships.""",
                context=""
            ) for doc in self.problem_text.split("Document ")[1:]]
        )

        # Step 3: Identify bridge entities and construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {entities_and_relationships}
            
            Construct a reasoning chain that connects the documents to answer the question.
            Identify bridge entities and follow the chain of relationships.""",
            context=question_type
        )

        # Step 4: Extract and validate the answer
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer from the following document:
                {doc}
                Ensure the answer is factually correct and supported by evidence.""",
                context=reasoning_chain
            ) for doc in self.problem_text.split("Document ")[1:]]
        )

        # Step 5: Resolve ambiguity using ensemble
        final_answer = await self.ensemble(
            instruction="Select the most plausible answer based on supporting evidence.",
            contexts_list=candidate_answers
        )

        return final_answer