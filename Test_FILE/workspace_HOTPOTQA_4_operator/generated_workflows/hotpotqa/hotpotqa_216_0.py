# Workflow ID: hotpotqa_216_0
# Benchmark: hotpotqa
# Data Indices: [115]

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

        # Initial analysis to classify the problem and identify key components
        initial_analysis = await self.generate(
            instruction="""Analyze the question structure:
            - Identify if it's a bridge, comparison, or compositional question.
            - Extract key entities, relationships, and constraints.
            - Provide a structured classification.""",
            context=""
        )

        # Parallel exploration of potential bridge entities and document connections
        document_entities = await asyncio.gather(
            *[self.generate(
                instruction=f"""For this document, extract relevant entities and their relationships:
                Document: {doc}""",
                context=""
            ) for doc in ["Document 1", "Document 2", "Document 3", "Document 4", "Document 5"]]
        )

        # Synthesize findings to identify common entities that serve as bridges
        bridge_entities = await self.ensemble(
            instruction="Identify common entities that serve as bridges across documents.",
            contexts_list=document_entities
        )

        # Conditional branching based on the identified question type
        if "bridge" in initial_analysis.lower():
            # Follow the chain of documents connected by bridge entities
            reasoning_chain = await self.generate(
                instruction=f"""Using the identified bridge entities: {bridge_entities}
                Follow the chain of documents to construct a logical reasoning flow.""",
                context=initial_analysis
            )
        elif "comparison" in initial_analysis.lower():
            # Compare properties across identified documents
            reasoning_chain = await self.generate(
                instruction=f"""Compare properties across the identified documents:
                Bridge Entities: {bridge_entities}""",
                context=initial_analysis
            )
        else:
            # Combinational questions require combining multiple facts
            reasoning_chain = await self.generate(
                instruction=f"""Combine multiple facts to derive the answer:
                Bridge Entities: {bridge_entities}""",
                context=initial_analysis
            )

        # Iterative refinement of the extracted information
        refined_reasoning = await self.revise(
            instruction="Improve clarity and accuracy of the reasoning chain.",
            context=reasoning_chain
        )

        summarized_reasoning = await self.summarize(
            instruction="Condense the refined reasoning into a concise summary.",
            context=refined_reasoning
        )

        # Final synthesis to extract the precise answer
        final_answer = await self.generate(
            instruction=f"""Formulate the final answer based on the synthesized information:
            Summary: {summarized_reasoning}""",
            context=refined_reasoning
        )

        # Ensure the final answer is precise and factually correct
        precise_answer = await self.revise(
            instruction="Ensure the final answer is precise and factually correct.",
            context=final_answer
        )

        return precise_answer