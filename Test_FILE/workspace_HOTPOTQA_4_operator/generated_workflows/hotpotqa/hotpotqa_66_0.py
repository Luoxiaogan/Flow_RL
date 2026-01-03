# Workflow ID: hotpotqa_66_0
# Benchmark: hotpotqa
# Data Indices: [9]

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
            - Bridge: Connects documents through shared entities.
            - Comparison: Compares properties across documents.
            - Compositional: Combines multiple facts.
            Provide clear classification with justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        entities = await self.generate(
            instruction="""Extract named entities and relationships from all documents:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Organizations: [names and descriptions]
            - Relationships: [connections between entities]""",
            context=""
        )

        # Step 3: Analyze documents in parallel to identify shared entities
        document_analysis_tasks = []
        for i in range(10):  # Assuming up to 10 documents
            task = self.generate(
                instruction=f"""Analyze Document {i+1}:
                - Identify key entities and their roles.
                - Highlight potential bridge entities.
                - Summarize main facts.""",
                context=entities
            )
            document_analysis_tasks.append(task)
        document_analyses = await asyncio.gather(*document_analysis_tasks)

        # Step 4: Synthesize reasoning chains
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize reasoning chains by connecting shared entities:
            - Identify bridge entities linking documents.
            - Construct logical sequences of facts.
            - Ensure each step is factually supported.""",
            contexts_list=document_analyses
        )

        # Step 5: Extract the precise answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            {reasoning_chain}
            - Ensure the answer is a short text span or yes/no response.
            - Verify factual correctness.""",
            context=reasoning_chain
        )

        # Step 6: Identify supporting facts
        supporting_facts = await self.generate(
            instruction=f"""Identify supporting facts from different documents:
            {reasoning_chain}
            - List facts that justify the answer.
            - Ensure each fact comes from a distinct document.""",
            context=reasoning_chain
        )

        # Final Output
        return {
            "question_type": question_type,
            "reasoning_chain": reasoning_chain,
            "answer": answer,
            "supporting_facts": supporting_facts
        }