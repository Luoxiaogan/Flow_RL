# Workflow ID: hotpotqa_15_0
# Benchmark: hotpotqa
# Data Indices: [465]

class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        """
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type as bridge, comparison, or compositional.
            2. Extract key entities mentioned in the question.
            3. Identify any specific constraints or conditions.
            Provide structured output with classification and entities.""",
            context=""
        )

        # Step 2: Entity Extraction & Document Mapping
        entities_and_mapping = await self.generate(
            instruction=f"""Given the analysis:
            {analysis}
            
            Extract all named entities from the context documents and map them to their respective documents.
            Format as structured list with categories:
            - Entities: [entity names]
            - Documents: [document titles where each entity appears]""",
            context=""
        )

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Using the entities and document mapping:
            {entities_and_mapping}
            
            Construct a reasoning chain that connects the entities across documents to answer the question.
            Provide step-by-step reasoning with references to specific sentences in the documents.""",
            context=entities_and_mapping
        )

        # Step 4: Answer Extraction
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer from the final document in the reasoning chain.
            Ensure the answer is a short text span or yes/no response as required.""",
            context=reasoning_chain
        )

        # Step 5: Validation & Refinement
        validation = await self.revise(
            instruction=f"""Validate the extracted answer:
            {answer_extraction}
            
            Check if the answer is supported by the facts in the documents.
            If not, refine the answer based on the supporting facts.""",
            context=answer_extraction
        )

        return validation