# Workflow ID: hotpotqa_130_0
# Benchmark: hotpotqa
# Data Indices: [403, 107]

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
            instruction="""Classify the question into one of the following types:
            - Bridge Question: Connects information through shared entities.
            - Comparison Question: Compares properties across documents.
            - Compositional Question: Combines multiple facts to derive the answer.
            Provide the classification along with a brief explanation.""",
            context=""
        )

        # Step 2: Identify bridge entities (parallel processing)
        document_analysis_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            document_analysis_tasks.append(
                self.generate(
                    instruction=f"""Extract all named entities from Document {i} that could serve as bridge entities.
                    Focus on entities that are relevant to the question and appear in multiple documents.
                    Format as a list of entities with their roles or relationships.""",
                    context=""
                )
            )
        bridge_entities_list = await asyncio.gather(*document_analysis_tasks)

        # Step 3: Select the most relevant bridge entity
        selected_entity = await self.ensemble(
            instruction="""Select the most relevant bridge entity that connects the documents and helps answer the question.
            Consider relevance to the question, frequency across documents, and logical consistency.""",
            contexts_list=bridge_entities_list
        )

        # Step 4: Construct the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the selected bridge entity: {selected_entity}
            Construct a logical reasoning chain that connects facts from different documents to answer the question.
            Ensure each fact is explicitly linked to the next and supported by evidence from the documents.""",
            context=""
        )

        # Step 5: Extract the precise answer
        extracted_answer = await self.generate(
            instruction=f"""Based on the reasoning chain: {reasoning_chain}
            Extract the precise answer to the question. The answer must be a short text span or yes/no response,
            directly taken from the documents without paraphrasing.""",
            context=""
        )

        # Step 6: Validate the answer against supporting facts
        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer: {extracted_answer}
            Cross-check it with the supporting facts provided in the documents.
            If discrepancies are found, suggest corrections or refinements.""",
            context=reasoning_chain
        )

        return validated_answer