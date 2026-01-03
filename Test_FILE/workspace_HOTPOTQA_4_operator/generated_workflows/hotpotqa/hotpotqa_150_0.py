# Workflow ID: hotpotqa_150_0
# Benchmark: hotpotqa
# Data Indices: [425, 226]

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
            1. Is it a bridge question, comparison question, or compositional question?
            2. What entities or concepts are involved?
            3. What is the expected answer format?
            Provide structured classification.""",
            context=""
        )

        # Step 2: Extract entities and facts from all documents in parallel
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        extraction_tasks = [
            self.generate(
                instruction=f"""Extract entities, relationships, and key facts from Document {i}:
                - Named entities (people, places, organizations)
                - Key relationships
                - Relevant facts""",
                context=doc
            ) for i, doc in enumerate(documents) if doc.strip()
        ]
        extracted_info = await asyncio.gather(*extraction_tasks)

        # Step 3: Construct reasoning chain based on question type
        reasoning_chain = await self.ensemble(
            instruction=f"""Construct reasoning chain based on question type:
            Question Type: {question_type}
            Extracted Information: {extracted_info}
            Identify connections between documents and build reasoning chain.""",
            contexts_list=extracted_info
        )

        # Step 4: Synthesize answer using reasoning chain
        answer = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            Extract the precise answer span from the relevant document.
            Ensure the answer is factually correct and matches the expected format.""",
            context=reasoning_chain
        )

        # Step 5: Validate and refine answer
        validated_answer = await self.revise(
            instruction="""Validate the answer:
            - Check factual correctness
            - Ensure precision
            - Improve clarity if necessary""",
            context=answer
        )

        return validated_answer