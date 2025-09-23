# Workflow ID: hotpotqa_233_0
# Benchmark: hotpotqa
# Data Indices: [296, 143]

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

        # Step 1: Question Classification
        question_analysis = await self.generate(
            instruction="""Analyze the question:
            - Classify the question type (bridge, comparison, compositional).
            - Extract key entities and relationships.
            - Identify what needs to be answered.""",
            context=""
        )

        # Step 2: Fact Extraction (Parallelized across documents)
        fact_extraction_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            task = self.generate(
                instruction=f"""Extract relevant facts from Document {i}:
                - Focus on entities and relationships mentioned in the question.
                - Include any potential bridge entities.""",
                context=question_analysis
            )
            fact_extraction_tasks.append(task)
        extracted_facts = await asyncio.gather(*fact_extraction_tasks)

        # Step 3: Bridge Entity Identification
        bridge_entities = await self.ensemble(
            instruction="""Identify bridge entities:
            - Compare facts across documents.
            - Find shared entities or relationships that connect documents.""",
            contexts_list=extracted_facts
        )

        # Step 4: Reasoning Chain Construction
        reasoning_chains = []
        for fact_set in extracted_facts:
            chain = await self.generate(
                instruction=f"""Build a reasoning chain using these facts:
                Facts: {fact_set}
                Bridge Entities: {bridge_entities}
                Connect facts across documents to answer the question.""",
                context=question_analysis
            )
            reasoning_chains.append(chain)

        # Step 5: Answer Extraction
        answers = []
        for chain in reasoning_chains:
            answer = await self.summarize(
                instruction="""Extract the precise answer:
                - Ensure the answer is concise and directly addresses the question.
                - Include supporting evidence from the reasoning chain.""",
                context=chain
            )
            refined_answer = await self.revise(
                instruction="Refine the answer for clarity and correctness.",
                context=answer
            )
            answers.append(refined_answer)

        # Step 6: Final Validation and Selection
        final_answer = await self.ensemble(
            instruction="""Select the best answer:
            - Ensure factual correctness.
            - Choose the most concise and well-supported answer.""",
            contexts_list=answers
        )

        return final_answer