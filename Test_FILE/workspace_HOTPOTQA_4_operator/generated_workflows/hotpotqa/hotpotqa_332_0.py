# Workflow ID: hotpotqa_332_0
# Benchmark: hotpotqa
# Data Indices: [320]

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
            - Bridge Question: Connects documents through shared entities (e.g., "What nationality is the director of [movie]?")
            - Comparison Question: Compares properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional Question: Combines multiple facts to derive an answer
            Provide a clear classification with reasoning.""",
            context=""
        )

        # Step 2: Extract and refine entities
        raw_entities = await self.generate(
            instruction=f"""Extract all named entities, relationships, and keywords from the question and documents.
            Focus on entities that could serve as bridge points between documents.
            Format as a structured list with categories:
            - People
            - Places
            - Organizations
            - Concepts""",
            context=classification
        )
        refined_entities = await self.revise(
            instruction="Refine the extracted entities to ensure relevance and remove noise.",
            context=raw_entities
        )

        # Step 3: Analyze documents in parallel
        document_analysis_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            task = self.generate(
                instruction=f"""Analyze Document {i} for information related to the refined entities:
                - Identify supporting facts
                - Highlight connections to other documents
                - Note any direct answers to the question""",
                context=refined_entities
            )
            document_analysis_tasks.append(task)
        document_analyses = await asyncio.gather(*document_analysis_tasks)

        # Step 4: Synthesize reasoning chain
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize the document analyses into a coherent reasoning chain:
            - Connect entities across documents
            - Build logical sequences of facts
            - Ensure all steps are supported by evidence""",
            contexts_list=document_analyses
        )

        # Step 5: Extract and validate answer
        raw_answer = await self.generate(
            instruction=f"""Using the reasoning chain, extract the precise answer to the question.
            Ensure the answer is a short text span or yes/no response.
            Include supporting facts for validation.""",
            context=reasoning_chain
        )
        validated_answer = await self.revise(
            instruction="Validate the extracted answer for factual correctness and alignment with the question.",
            context=raw_answer
        )

        # Step 6: Feedback loop for completeness
        evaluation = await self.generate(
            instruction=f"""Evaluate the completeness of the reasoning chain and answer:
            - Are all steps logically connected?
            - Is the answer fully supported by evidence?
            - Are there any gaps or ambiguities?""",
            context=validated_answer
        )
        if "incomplete" in evaluation.lower() or "gap" in evaluation.lower():
            # Trigger re-computation
            return await self.run_workflow()
        else:
            return validated_answer