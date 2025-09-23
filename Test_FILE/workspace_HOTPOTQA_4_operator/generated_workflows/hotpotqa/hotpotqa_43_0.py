# Workflow ID: hotpotqa_43_0
# Benchmark: hotpotqa
# Data Indices: [408, 448]

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
            instruction="Classify the question type into one of the following categories: "
                        "1. Bridge Questions (connect documents through shared entities), "
                        "2. Comparison Questions (compare attributes across documents), "
                        "3. Compositional Questions (combine multiple facts). "
                        "Provide reasoning for your classification.",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        entities = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract named entities, relationships, and key phrases from the following document: {doc}",
                context=""
            ) for doc in ["Document 1", "Document 2", "Document 3", "Document 4", "Document 5"]]
        )
        entity_summary = "\n".join(entities)

        # Step 3: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"Based on the question type ({question_type}) and extracted entities ({entity_summary}), "
                        "construct a reasoning chain that connects the documents to answer the question. "
                        "Include intermediate steps and supporting facts.",
            context=entity_summary
        )

        # Step 4: Validate reasoning chain
        validation = await self.revise(
            instruction=f"Validate the reasoning chain ({reasoning_chain}) against the original documents. "
                        "Ensure factual accuracy and logical consistency. Provide corrections if needed.",
            context=reasoning_chain
        )

        # Step 5: Extract and format the final answer
        final_answer = await self.generate(
            instruction=f"Extract the final answer from the validated reasoning chain ({validation}). "
                        "Format the answer as a short text span or yes/no response. Include supporting facts if required.",
            context=validation
        )

        return final_answer