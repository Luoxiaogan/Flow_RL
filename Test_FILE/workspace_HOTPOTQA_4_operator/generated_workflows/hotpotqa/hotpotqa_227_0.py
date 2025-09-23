# Workflow ID: hotpotqa_227_0
# Benchmark: hotpotqa
# Data Indices: [309]

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

        # Phase 1: Initial Analysis
        classification = await self.generate(
            instruction="""Analyze the question to determine its type:
            - Is it a bridge question, comparison question, or compositional question?
            - Identify potential bridge entities or concepts.
            Provide a structured classification.""",
            context=""
        )
        summarized_classification = await self.summarize(
            instruction="Condense the classification into key points.",
            context=classification
        )

        # Phase 2: Document Exploration
        document_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract relevant facts and entities from {doc_title}. Focus on connections to the question and identified bridge entities.",
                context=summarized_classification
            ) for doc_title in ["Document 1", "Document 2", "Document 3", "Document 4", "Document 5"]]
        )
        bridge_entity = await self.ensemble(
            instruction="Identify the most relevant bridge entity or concept that connects the documents.",
            contexts_list=document_facts
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Using the bridge entity '{bridge_entity}', construct a reasoning chain:
            - Start with the question.
            - Follow the logical connections between documents.
            - End with the answer.
            Ensure the chain is complete and logically consistent.""",
            context=summarized_classification
        )
        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity, accuracy, and completeness.",
            context=reasoning_chain
        )

        # Phase 4: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer span and supporting evidence from the reasoning chain:
            - Ensure the answer is a short text span or yes/no response.
            - Identify the supporting facts from specific documents.""",
            context=refined_chain
        )
        validated_answer = await self.revise(
            instruction="Validate the answer against the reasoning chain and supporting evidence.",
            context=answer_extraction
        )

        return validated_answer