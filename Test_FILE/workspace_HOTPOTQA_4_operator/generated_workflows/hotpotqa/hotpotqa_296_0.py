# Workflow ID: hotpotqa_296_0
# Benchmark: hotpotqa
# Data Indices: [25, 83]

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
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining facts)?
            Provide a clear classification with reasoning.""",
            context=""
        )

        # Step 2: Extract key entities and relationships from documents
        async def extract_entities(doc_id):
            return await self.generate(
                instruction=f"""Extract key entities and relationships from Document {doc_id}:
                - Named entities (people, places, organizations)
                - Numbers and their roles
                - Relevant sentences or phrases""",
                context=""
            )

        document_ids = [f"Document {i+1}" for i in range(10)]  # Assuming up to 10 documents
        entities_list = await asyncio.gather(*[extract_entities(doc_id) for doc_id in document_ids])

        # Summarize extracted entities
        summarized_entities = await self.summarize(
            instruction="Condense the extracted entities into a structured list.",
            context="\n".join(entities_list)
        )

        # Step 3: Build the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Based on the question type ({question_type}) and extracted entities:
            - Identify shared entities or relationships
            - Construct a reasoning chain connecting facts across documents
            - Ensure each step is logically sound and factually supported""",
            context=summarized_entities
        )

        # Refine the reasoning chain
        refined_chain = await self.revise(
            instruction="Improve clarity, accuracy, and completeness of the reasoning chain.",
            context=reasoning_chain
        )

        # Step 4: Extract the precise answer
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction="Extract the exact text span or yes/no response from the reasoning chain.",
                context=refined_chain
            ),
            self.generate(
                instruction="Validate the extracted answer against supporting facts.",
                context=refined_chain
            )
        )

        # Ensemble to select the best answer
        final_answer = await self.ensemble(
            instruction="Select the most accurate and well-supported answer.",
            contexts_list=answer_candidates
        )

        return final_answer