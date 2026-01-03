# Workflow ID: hotpotqa_41_0
# Benchmark: hotpotqa
# Data Indices: [349, 258]

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
        
        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify all named entities (people, places, organizations).
            3. Highlight relationships or constraints implied by the question.
            Provide a structured breakdown.""",
            context=""
        )
        
        # Step 2: Parallel Entity Search
        entities = await self.generate(
            instruction="Extract all named entities mentioned in the question.",
            context=analysis
        )
        entity_search_tasks = [
            self.generate(
                instruction=f"Search for mentions of '{entity}' in this document and extract relevant sentences.",
                context=document
            ) for entity in entities.split(",") for document in ["Document 1", "Document 2", "Document 3"]  # Dynamically fetch all documents
        ]
        entity_results = await asyncio.gather(*entity_search_tasks)
        
        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.ensemble(
            instruction="Identify the most promising connections between documents and construct a reasoning chain.",
            contexts_list=entity_results
        )
        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity, logical consistency, and factual accuracy.",
            context=reasoning_chain
        )
        
        # Step 4: Answer Extraction and Validation
        answer = await self.summarize(
            instruction="Extract the precise answer span from the reasoning chain.",
            context=refined_chain
        )
        validated_answer = await self.revise(
            instruction="Validate the answer against the question to ensure it meets the required format and is factually correct.",
            context=answer
        )
        
        return validated_answer