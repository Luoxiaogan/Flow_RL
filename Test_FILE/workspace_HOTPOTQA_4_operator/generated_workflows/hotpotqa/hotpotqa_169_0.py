# Workflow ID: hotpotqa_169_0
# Benchmark: hotpotqa
# Data Indices: [68, 455]

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

        # Step 1: Initial Analysis - Classify question type and extract high-level entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type (bridge, comparison, compositional).
            Extract high-level entities and relationships mentioned in the question.
            Provide a structured output including:
            - Question Type: [bridge/comparison/compositional]
            - Key Entities: [list of entities]
            - Relationships: [list of relationships]""",
            context=""
        )

        # Step 2: Parallel Entity and Relationship Extraction from Documents
        documents = re.findall(r"Document \d+:.*?(?=\n\nDocument|\Z)", self.problem_text, re.DOTALL)
        extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities and relationships from the following document:
                {doc}
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ) for doc in documents
        ]
        extracted_data = await asyncio.gather(*extraction_tasks)

        # Step 3: Reasoning Chain Construction - Identify bridge entities and connect documents
        reasoning_chain = await self.ensemble(
            instruction="""Identify bridge entities that connect different documents.
            Construct a reasoning chain by following these bridge entities across documents.
            Provide a detailed explanation of the reasoning chain, including:
            - Bridge Entities: [list of entities]
            - Document Connections: [how documents are connected]
            - Final Document: [document containing the answer]""",
            contexts_list=extracted_data
        )

        # Step 4: Answer Extraction and Validation
        final_answer = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer from the final document.
            Ensure the answer is factually correct and matches the expected format (short text span or yes/no).""",
            context=""
        )

        # Step 5: Iterative Refinement (Optional)
        for _ in range(2):  # Limit iterations to avoid infinite loops
            validation = await self.revise(
                instruction=f"""Validate the extracted answer:
                {final_answer}
                
                Check against supporting facts from the documents.
                Refine the answer if necessary, ensuring it is precise and supported by evidence.""",
                context=reasoning_chain
            )
            if "error" not in validation.lower():
                break
            final_answer = validation

        return final_answer