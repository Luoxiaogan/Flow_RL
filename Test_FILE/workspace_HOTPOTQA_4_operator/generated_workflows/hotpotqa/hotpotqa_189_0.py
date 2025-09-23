# Workflow ID: hotpotqa_189_0
# Benchmark: hotpotqa
# Data Indices: [369, 488]

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

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question into one of the following categories:
            1. Bridge Question: Requires connecting information across documents via shared entities.
            2. Comparison Question: Involves comparing properties or attributes across documents.
            3. Compositional Question: Demands combining multiple facts to derive the answer.
            Provide a clear classification with justification.""",
            context=""
        )

        # Step 2: Extract entities and identify bridge entities
        entities_extraction = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract named entities and key phrases from the following document:
                {doc}
                Focus on people, places, organizations, and significant concepts.""",
                context=""
            ) for doc in self.extract_documents()]
        )
        bridge_entities = await self.generate(
            instruction=f"""Identify bridge entities that appear in multiple documents.
            Entities: {entities_extraction}
            Highlight entities that connect documents and explain their relevance.""",
            context=""
        )

        # Step 3: Build the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain to answer the question:
            Question Type: {question_type}
            Bridge Entities: {bridge_entities}
            Connect documents through shared entities and outline the logical path to the answer.""",
            context=""
        )

        # Step 4: Refine the reasoning chain
        refined_chain = await self.revise(
            instruction=f"""Improve clarity and accuracy of the reasoning chain:
            Original Chain: {reasoning_chain}
            Ensure all connections are factually correct and logically sound.""",
            context=reasoning_chain
        )

        # Step 5: Extract and verify the answer
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer from the following document:
                {doc}
                Reasoning Chain: {refined_chain}
                Provide the exact answer span that addresses the question.""",
                context=""
            ) for doc in self.extract_documents()]
        )
        final_answer = await self.ensemble(
            instruction=f"""Select the most accurate and factually correct answer:
            Candidate Answers: {candidate_answers}
            Cross-reference with supporting facts from multiple documents.""",
            contexts_list=candidate_answers
        )

        return final_answer

    def extract_documents(self):
        # Helper function to extract document texts from the problem text
        import re
        pattern = r"Document \d+:.*?\n(.*?)\n\n"
        return re.findall(pattern, self.problem_text, re.DOTALL)