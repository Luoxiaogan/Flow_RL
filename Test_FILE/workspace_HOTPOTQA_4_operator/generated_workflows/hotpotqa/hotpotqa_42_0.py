# Workflow ID: hotpotqa_42_0
# Benchmark: hotpotqa
# Data Indices: [262, 346]

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
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Requires connecting two entities through a shared attribute.
            2. Comparison Question: Requires evaluating properties across multiple documents.
            3. Compositional Question: Requires combining multiple facts to derive the answer.
            Provide structured analysis with clear reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        async def extract_entities(doc_name):
            return await self.generate(
                instruction=f"""Extract all named entities, key phrases, and their relationships from {doc_name}.
                Focus on entities that are likely to form connections or serve as points of comparison.
                Format as a structured list with categories: People, Places, Numbers, Actions.""",
                context=""
            )

        doc_titles = ["Document 1", "Document 2", "Document 3", "Document 4", "Document 5", 
                      "Document 6", "Document 7", "Document 8", "Document 9", "Document 10"]
        entity_extraction_tasks = [extract_entities(title) for title in doc_titles]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Identify the most promising connections
        connections = await self.ensemble(
            instruction="""Identify the most promising connections between the extracted entities:
            - Look for shared entities that link multiple documents.
            - Identify attributes that can be compared across documents.
            - Highlight entities that are central to the question.""",
            contexts_list=extracted_entities
        )

        # Step 4: Construct the reasoning chain based on question type
        reasoning_chain = ""
        if "Bridge Question" in classification:
            reasoning_chain = await self.generate(
                instruction=f"""Construct a reasoning chain for the bridge question:
                - Identify the shared entity that connects the relevant documents.
                - Follow the logical chain to arrive at the answer.
                Connections: {connections}""",
                context=""
            )
        elif "Comparison Question" in classification:
            reasoning_chain = await self.generate(
                instruction=f"""Construct a reasoning chain for the comparison question:
                - Identify the attributes being compared.
                - Determine which document provides the necessary information.
                Connections: {connections}""",
                context=""
            )
        else:  # Compositional Question
            reasoning_chain = await self.generate(
                instruction=f"""Construct a reasoning chain for the compositional question:
                - Combine multiple facts from the documents to derive the answer.
                Connections: {connections}""",
                context=""
            )

        # Step 5: Extract and validate the final answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the relevant document based on the reasoning chain:
            - Ensure the answer is factually correct and directly supported by the evidence.
            Reasoning Chain: {reasoning_chain}""",
            context=""
        )

        # Iterative validation loop
        for _ in range(3):  # Allow up to 3 iterations for refinement
            validation = await self.revise(
                instruction=f"""Validate the answer for factual accuracy and precision:
                - Check if the answer is supported by the reasoning chain.
                - Highlight any discrepancies or ambiguities.
                Current Answer: {answer}""",
                context=reasoning_chain
            )
            if "error" not in validation.lower():
                break
            answer = await self.revise(
                instruction=f"""Revise the answer to address the following issues:
                {validation}
                Original Answer: {answer}""",
                context=reasoning_chain
            )

        return answer