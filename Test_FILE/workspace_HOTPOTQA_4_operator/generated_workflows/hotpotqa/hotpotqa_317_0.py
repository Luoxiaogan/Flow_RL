# Workflow ID: hotpotqa_317_0
# Benchmark: hotpotqa
# Data Indices: [142]

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

        # Step 1: Problem Analysis and Entity Extraction
        entity_analysis = await self.generate(
            instruction="""Analyze the problem and documents:
            - Identify key entities (people, places, events, etc.)
            - Extract relationships between entities
            - Highlight potential bridge entities that connect documents
            Provide a structured list of entities and their roles.""",
            context=""
        )

        # Step 2: Question Type Classification
        classification_perspectives = await asyncio.gather(
            self.generate(instruction="Classify the question based on logical structure...", context=entity_analysis),
            self.generate(instruction="Classify the question based on keyword patterns...", context=entity_analysis),
            self.generate(instruction="Classify the question based on required reasoning steps...", context=entity_analysis)
        )
        question_type = await self.ensemble(
            instruction="Determine the most likely question type (bridge, comparison, compositional)...",
            contexts_list=classification_perspectives
        )

        # Step 3: Bridge Entity Identification
        bridge_candidates = await asyncio.gather(
            *[self.generate(instruction=f"Identify bridge entities from document {i+1}...", context=doc)
              for i, doc in enumerate(entity_analysis.split('Document')) if doc.strip()]
        )
        bridge_entity = await self.ensemble(
            instruction="Select the most relevant bridge entity connecting the documents...",
            contexts_list=bridge_candidates
        )

        # Step 4: Evidence Chain Construction
        evidence_chain = ""
        for doc in entity_analysis.split('Document'):
            if doc.strip():
                hypothesis = await self.generate(
                    instruction=f"Generate a hypothesis about this document's contribution to the answer: {doc}",
                    context=evidence_chain
                )
                refined_hypothesis = await self.revise(
                    instruction="Refine the hypothesis based on accumulated context...",
                    context=hypothesis
                )
                evidence_chain += f"\n{refined_hypothesis}"

        # Step 5: Answer Extraction and Validation
        candidate_answer = await self.generate(
            instruction=f"Extract the precise answer from the final document based on the evidence chain: {evidence_chain}",
            context=""
        )
        final_answer = await self.revise(
            instruction="Ensure the answer is an exact match from the source text and validate against the evidence chain...",
            context=candidate_answer
        )

        return final_answer