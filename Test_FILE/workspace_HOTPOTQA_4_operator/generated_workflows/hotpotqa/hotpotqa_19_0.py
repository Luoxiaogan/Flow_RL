# Workflow ID: hotpotqa_19_0
# Benchmark: hotpotqa
# Data Indices: [126]

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
            1. Bridge: Requires connecting documents through shared entities.
            2. Comparison: Requires comparing properties across documents.
            3. Compositional: Requires combining multiple facts to derive an answer.
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        async def extract_entities(document_title):
            return await self.generate(
                instruction=f"""Extract all named entities, relationships, and key facts from the document titled '{document_title}'.
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )
        
        # Extract entities in parallel
        document_titles = ["Alexander Ivanovich Mikhailov", "Lazar Lyusternik", "Alexander Achziger", "Alexander Adashev", 
                           "Sparse grid", "Alexander Marinesko", "Alexander Todorsky", "Alexander Medvedev", 
                           "Alexander Ivanovich Konovalov", "Alexander Polezhayev"]
        entity_results = await asyncio.gather(*[extract_entities(title) for title in document_titles])

        # Step 3: Build reasoning chain based on question type
        reasoning_chain = await self.ensemble(
            instruction=f"""Based on the question type ({question_type}) and extracted entities:
            {entity_results}
            
            Build a reasoning chain that connects documents through shared entities or logical relationships.
            Provide the chain as a sequence of steps, citing specific documents and facts.""",
            contexts_list=entity_results
        )

        # Step 4: Extract the precise answer
        answer = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span or yes/no response.
            Ensure the answer is factually correct and supported by the documents.""",
            context=reasoning_chain
        )

        # Step 5: Validate and refine the answer
        validated_answer = await self.revise(
            instruction=f"""Validate the answer:
            {answer}
            
            Ensure it is factually correct, directly addresses the question, and is supported by the reasoning chain.
            Refine if necessary.""",
            context=answer
        )

        return validated_answer