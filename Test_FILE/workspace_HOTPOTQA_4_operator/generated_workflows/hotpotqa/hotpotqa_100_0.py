# Workflow ID: hotpotqa_100_0
# Benchmark: hotpotqa
# Data Indices: [443]

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

        # Step 1: Analyze the question to classify its type and extract key entities
        question_analysis = await self.generate(
            instruction="""Analyze the question to:
            1. Classify its type (bridge, comparison, compositional).
            2. Extract key entities and phrases.
            3. Identify potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )

        # Step 2: Extract relevant information from each document in parallel
        document_contexts = []
        for i in range(1, 11):  # Assuming up to 10 documents
            doc_analysis = await self.generate(
                instruction=f"""Extract all named entities, relationships, and key facts from Document {i}.
                Focus on information relevant to the question: {question_analysis}.
                Format as structured list.""",
                context=""
            )
            document_contexts.append(doc_analysis)

        # Step 3: Build reasoning chains by synthesizing information
        reasoning_chain = await self.ensemble(
            instruction=f"""Synthesize information from all documents to build reasoning chains:
            - Question Type: {question_analysis}
            - Documents: {document_contexts}
            Construct coherent chains connecting relevant facts across documents.""",
            contexts_list=document_contexts
        )

        # Step 4: Generate and validate the answer
        candidate_answer = await self.generate(
            instruction=f"""Based on the reasoning chain: {reasoning_chain},
            generate a precise answer to the question.
            Ensure the answer matches the expected format (short text span or yes/no).""",
            context=reasoning_chain
        )

        refined_answer = await self.revise(
            instruction=f"""Validate and refine the candidate answer: {candidate_answer}.
            Ensure factual accuracy and match the expected format.
            Correct any errors or ambiguities.""",
            context=candidate_answer
        )

        # Step 5: Extract supporting facts
        supporting_facts = await self.generate(
            instruction=f"""Identify specific sentences from the documents that support the answer: {refined_answer}.
            Provide references to document titles and sentence IDs.""",
            context=reasoning_chain
        )

        return {
            "answer": refined_answer,
            "supporting_facts": supporting_facts
        }