# Workflow ID: hotpotqa_279_0
# Benchmark: hotpotqa
# Data Indices: [53]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional).
            Identify key entities and their relationships.
            Determine which documents are most relevant to the question.""",
            context=""
        )

        # Phase 2: Document Exploration (Parallel)
        entities = await self.generate(
            instruction=f"""Extract named entities and key facts from the documents.
            Focus on entities related to: {analysis}.
            Format as structured list with categories: [Entity, Document, Fact].""",
            context=analysis
        )
        entity_list = entities.split("\n")  # Simplified parsing for demonstration

        # Parallel extraction of relevant facts
        fact_extraction_tasks = [
            self.generate(
                instruction=f"""From {entity}, extract all relevant facts.
                Focus on numerical data, relationships, and comparisons.""",
                context=entities
            ) for entity in entity_list
        ]
        extracted_facts = await asyncio.gather(*fact_extraction_tasks)

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Build a reasoning chain using the extracted facts: {extracted_facts}.
            Connect the facts logically to answer the question.
            Highlight any ambiguities or missing information.""",
            context="\n".join(extracted_facts)
        )

        # Validate and refine the reasoning chain
        refined_chain = await self.revise(
            instruction="""Check the reasoning chain for consistency and completeness.
            Resolve ambiguities and fill gaps if possible.""",
            context=reasoning_chain
        )

        # Phase 4: Answer Extraction
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the final answer from the reasoning chain: {refined_chain}.
                Ensure the answer is a short factual span or yes/no response.""",
                context=refined_chain
            ),
            self.generate(
                instruction=f"""Cross-check the reasoning chain against the original documents.
                Extract an alternative answer if discrepancies are found.""",
                context=refined_chain
            )
        )

        # Ensemble Decision-Making
        final_answer = await self.ensemble(
            instruction="""Select the most accurate and well-supported answer.
            Resolve conflicts between candidates based on evidence.""",
            contexts_list=candidate_answers
        )

        return final_answer