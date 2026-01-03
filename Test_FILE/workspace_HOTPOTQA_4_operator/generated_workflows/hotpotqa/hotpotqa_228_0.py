# Workflow ID: hotpotqa_228_0
# Benchmark: hotpotqa
# Data Indices: [360]

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
        classification = await self.generate(
            instruction="""Classify this question into one of the following types:
            - Bridge: Requires connecting documents through shared entities.
            - Comparison: Requires comparing properties across documents.
            - Compositional: Requires combining multiple facts to derive an answer.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        async def extract_entities(doc_title):
            return await self.generate(
                instruction=f"""Extract all named entities and their relationships from the document titled "{doc_title}".
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )

        # Identify all document titles
        doc_titles = []
        for line in self.problem_text.split("\n"):
            if line.startswith("Document") and ":" in line:
                title = line.split(":")[1].strip()
                doc_titles.append(title)

        # Parallel entity extraction
        entities_list = await asyncio.gather(*[extract_entities(title) for title in doc_titles])

        # Step 3: Identify bridge entities
        bridge_entities = await self.generate(
            instruction=f"""Analyze the extracted entities from all documents:
            {entities_list}
            
            Identify potential bridge entities that connect multiple documents.
            Provide a ranked list of bridge entities with explanations.""",
            context=""
        )

        # Step 4: Construct reasoning chains
        reasoning_chains = await self.generate(
            instruction=f"""Using the identified bridge entities:
            {bridge_entities}
            
            Construct reasoning chains that connect documents to answer the question:
            {classification}
            
            Provide detailed reasoning chains with supporting facts.""",
            context=""
        )

        # Step 5: Extract and validate the answer
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the precise answer from the reasoning chain:
                {reasoning_chains}
                
                Ensure the answer is factually correct and matches the question format.""",
                context=""
            ),
            self.generate(
                instruction=f"""Provide an alternative interpretation of the reasoning chain:
                {reasoning_chains}
                
                Extract a different possible answer if applicable.""",
                context=""
            )
        )

        # Step 6: Select the best answer
        final_answer = await self.ensemble(
            instruction="""Select the best answer from the candidates:
            - Ensure factual correctness.
            - Match the question format.
            - Validate against supporting facts.""",
            contexts_list=candidate_answers
        )

        return final_answer