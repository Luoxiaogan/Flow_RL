# Workflow ID: hotpotqa_64_0
# Benchmark: hotpotqa
# Data Indices: [410, 317]

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
            instruction="""Classify the question into one of the following categories:
            1. Bridge Question: Requires connecting information through shared entities.
            2. Comparison Question: Involves comparing attributes across documents.
            3. Compositional Question: Combines multiple facts to derive an answer.
            Provide a structured classification with supporting reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        async def extract_entities(doc_id):
            return await self.generate(
                instruction=f"""Extract named entities, relationships, and key phrases from Document {doc_id}.
                Focus on entities that could serve as bridge concepts.
                Format as a structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]""",
                context=""
            )

        # Assume there are N documents; adjust dynamically based on input
        num_documents = 10  # Example: Adjust based on actual input
        entity_extraction_tasks = [extract_entities(i + 1) for i in range(num_documents)]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Build reasoning chains
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities:
            {extracted_entities}
            
            Construct a reasoning chain that connects the entities across documents to answer the question:
            {question_type}
            Provide a step-by-step explanation of how the entities relate to each other.""",
            context=""
        )

        # Step 4: Validate and extract the answer
        async def validate_answer(entity):
            return await self.generate(
                instruction=f"""Validate whether the entity '{entity}' is the correct answer.
                Check for factual consistency across documents and provide supporting evidence.""",
                context=reasoning_chain
            )

        candidate_answers = reasoning_chain.split('\n')  # Simplified extraction
        validation_tasks = [validate_answer(ans) for ans in candidate_answers]
        validated_answers = await asyncio.gather(*validation_tasks)

        # Step 5: Ensemble to select the best answer
        final_answer = await self.ensemble(
            instruction="Select the most factually consistent and well-supported answer.",
            contexts_list=validated_answers
        )

        return final_answer