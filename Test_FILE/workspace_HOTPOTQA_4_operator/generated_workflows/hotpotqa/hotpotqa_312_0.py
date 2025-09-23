# Workflow ID: hotpotqa_312_0
# Benchmark: hotpotqa
# Data Indices: [454]

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

        # Step 1: Analyze the problem and classify the question type
        analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            - Bridge: Connects entities across documents
            - Comparison: Compares properties across documents
            - Compositional: Combines multiple facts to derive the answer
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships from the context documents
        entities = await self.generate(
            instruction=f"""Extract all named entities, relationships, and key facts from the context documents.
            Format as a structured list:
            - Entities: [names and roles]
            - Relationships: [connections between entities]
            - Key Facts: [important sentences or phrases]""",
            context=analysis
        )

        # Step 3: Identify potential bridge entities and construct reasoning chains
        bridge_candidates = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {entities}
            
            Identify potential bridge entities that connect the target entities in the question.
            For each candidate, construct a reasoning chain that links the entities across documents.""",
            context=entities
        )

        # Evaluate and select the most plausible reasoning chain
        reasoning_chain = await self.ensemble(
            instruction=f"""Evaluate the reasoning chains:
            {bridge_candidates}
            
            Select the most plausible chain based on factual accuracy and logical coherence.""",
            contexts_list=bridge_candidates.split("\n\n")
        )

        # Step 4: Extract the precise answer from the relevant document
        answer = await self.generate(
            instruction=f"""Using the selected reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer from the relevant document.
            Ensure the answer is factually correct and directly supported by the documents.""",
            context=reasoning_chain
        )

        # Step 5: Validate and refine the answer
        refined_answer = await self.revise(
            instruction=f"""Validate the answer:
            {answer}
            
            Ensure it is factually correct, concise, and supported by the documents.
            If necessary, refine the answer to improve clarity or precision.""",
            context=answer
        )

        return refined_answer