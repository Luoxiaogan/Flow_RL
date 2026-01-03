# Workflow ID: hotpotqa_84_0
# Benchmark: hotpotqa
# Data Indices: [235, 348]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (e.g., bridge, comparison, compositional).
            Extract key entities, relationships, and constraints from the context documents.
            Format the output as:
            - Question Type: [type]
            - Entities: [list of entities]
            - Relationships: [list of relationships]""",
            context=""
        )

        # Step 2: Parallel Entity Matching - Identify bridge entities in each document
        entities_per_doc = await asyncio.gather(
            *[self.generate(
                instruction=f"""From the document titled '{doc_title}', extract entities and relationships.
                Focus on entities that could serve as bridge entities.
                Format as:
                - Entities: [list]
                - Relationships: [list]""",
                context=""
            ) for doc_title in ["Document 1", "Document 2", "Document 3"]]
        )

        # Step 3: Conditional Branching Based on Question Type
        if "comparison" in initial_analysis.lower():
            reasoning_strategy = "Compare shared attributes (e.g., dates, locations) across entities."
        elif "bridge" in initial_analysis.lower():
            reasoning_strategy = "Connect entities through shared relationships or attributes."
        else:
            reasoning_strategy = "Combine multiple facts to derive the answer."

        # Step 4: Ensemble Evidence Synthesis - Build reasoning chain
        reasoning_chain = await self.ensemble(
            instruction=f"""Synthesize evidence from the following entities and relationships:
            {entities_per_doc}
            Use the reasoning strategy: {reasoning_strategy}
            Construct an explicit reasoning chain that connects the documents.
            Highlight supporting facts for each step.""",
            contexts_list=entities_per_doc
        )

        # Step 5: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            {reasoning_chain}
            Ensure the answer is a short text span or yes/no response.
            Validate the answer against the supporting facts.""",
            context=reasoning_chain
        )

        # Step 6: Iterative Refinement (Optional Feedback Loop)
        refined_answer = await self.revise(
            instruction="Refine the answer for clarity, precision, and factual correctness.",
            context=answer_extraction
        )

        return refined_answer