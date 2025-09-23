# Workflow ID: hotpotqa_170_0
# Benchmark: hotpotqa
# Data Indices: [366]

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

        # Step 1: Initial Analysis - Classify question type and identify key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities and relationships.
            3. Highlight any constraints or conditions.
            Provide structured output.""",
            context=""
        )

        # Step 2: Entity and Evidence Extraction - Parallel exploration
        entities = await self.generate(
            instruction=f"""Extract all relevant entities from the documents:
            {initial_analysis}
            
            Focus on entities that connect documents or relate to the question.
            Format as a list of entities with descriptions.""",
            context=initial_analysis
        )

        evidence_tasks = [
            self.generate(
                instruction=f"""Find supporting facts for entity: {entity}
                Search all documents for sentences containing this entity.
                Include only sentences directly relevant to the question.""",
                context=entities
            )
            for entity in entities.split("\n") if entity.strip()
        ]
        evidence_results = await asyncio.gather(*evidence_tasks)

        # Step 3: Reasoning Chain Construction - Merge evidence
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize the evidence into a coherent reasoning chain:
            1. Connect entities across documents.
            2. Build a logical sequence leading to the answer.
            3. Highlight any gaps or ambiguities.""",
            contexts_list=evidence_results
        )

        # Step 4: Answer Synthesis and Validation
        final_answer = await self.generate(
            instruction=f"""Based on the reasoning chain:
            {reasoning_chain}
            
            Extract the final answer:
            1. Ensure it is factually correct.
            2. Use exact answer spans from the text.
            3. Flag any uncertainties or missing information.""",
            context=reasoning_chain
        )

        return final_answer