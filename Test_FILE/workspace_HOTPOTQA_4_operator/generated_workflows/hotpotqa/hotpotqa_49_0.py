# Workflow ID: hotpotqa_49_0
# Benchmark: hotpotqa
# Data Indices: [223, 412]

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
        import re

        # Step 1: Initial Analysis and Question Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify the question type:
            - Identify if it's a bridge, comparison, or compositional question
            - Extract key entities (names, places, dates)
            - Identify potential bridge entities (if applicable)
            Provide structured output with clear categories.""",
            context=""
        )

        # Parse initial analysis to extract entities and question type
        question_type = "bridge" if "bridge" in initial_analysis.lower() else \
                        "comparison" if "comparison" in initial_analysis.lower() else "compositional"
        entities = re.findall(r'\b[A-Z][a-zA-Z]*\b', initial_analysis)  # Simplified entity extraction

        # Step 2: Document Filtering and Entity Linking
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for mentions of entities: {', '.join(entities)}.
                - Identify relationships between entities
                - Extract supporting sentences
                - Note any ambiguities or conflicts""",
                context=doc
            ) for doc in ["Document 1", "Document 2", "Document 3"]]  # Example documents
        )
        reasoning_chain = await self.ensemble(
            instruction="Synthesize findings into a coherent reasoning chain connecting entities.",
            contexts_list=document_analyses
        )

        # Step 3: Evidence Chain Validation
        validated_chain = await self.revise(
            instruction="""Validate the reasoning chain:
            - Ensure each step is supported by explicit facts
            - Resolve ambiguities or conflicts
            - Maintain logical consistency""",
            context=reasoning_chain
        )

        # Step 4: Answer Extraction and Finalization
        final_answer = await self.generate(
            instruction=f"""Extract the precise answer from the validated reasoning chain:
            - Locate the exact sentence or phrase containing the answer
            - Format the answer as a short text span or yes/no""",
            context=validated_chain
        )

        return final_answer