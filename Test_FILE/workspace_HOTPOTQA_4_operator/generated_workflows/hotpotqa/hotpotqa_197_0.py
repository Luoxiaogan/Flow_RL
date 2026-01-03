# Workflow ID: hotpotqa_197_0
# Benchmark: hotpotqa
# Data Indices: [498]

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

        # Step 1: Initial Problem Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type (bridge, comparison, compositional).
            Extract key entities and classify their roles (e.g., person, place, concept).
            Focus on identifying bridge entities that connect documents.
            Provide structured output with clear labels for entities and their relationships.""",
            context=""
        )

        # Step 2: Parallel Document Exploration
        entities = initial_analysis.split("\n")  # Simplified parsing for entities
        document_tasks = [
            self.generate(
                instruction=f"""Analyze this document for mentions of the following entities: {', '.join(entities)}.
                Identify relevant sentences and relationships between entities.
                Provide structured output with document title, sentences, and relationships.""",
                context=document
            ) for document in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document")
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.ensemble(
            instruction="""Evaluate all document analyses to construct a reasoning chain.
            Connect entities across documents logically.
            Prioritize chains supported by multiple documents.
            Provide a clear explanation of the reasoning process.""",
            contexts_list=document_results
        )

        # Step 4: Answer Extraction
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain: {reasoning_chain}
            Extract the precise answer span from the final document.
            Ensure the answer is factually correct and supported by evidence.""",
            context=reasoning_chain
        )

        # Step 5: Validation and Refinement
        refined_answer = await self.revise(
            instruction="""Verify the answer for factual accuracy and logical coherence.
            Cross-reference with supporting facts from multiple documents.
            Clarify any ambiguities or contradictions.""",
            context=answer_extraction
        )

        # Step 6: Summarize Supporting Facts
        supporting_facts = await self.summarize(
            instruction="""Condense the supporting facts into a concise summary.
            Highlight key sentences and relationships that justify the answer.""",
            context=reasoning_chain
        )

        return {
            "answer": refined_answer.strip(),
            "supporting_facts": supporting_facts.strip()
        }