# Workflow ID: hotpotqa_5_0
# Benchmark: hotpotqa
# Data Indices: [301, 288]

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
            - Bridge: Requires connecting entities across documents
            - Comparison: Involves comparing properties
            - Compositional: Combines multiple facts
            Provide a clear classification and justification.""",
            context=""
        )
        
        # Step 2: Extract entities and relationships
        entities_and_relationships = await self.generate(
            instruction=f"""Extract key entities and relationships from the documents:
            - Entities: People, organizations, dates, concepts
            - Relationships: How entities interact
            Focus on information relevant to the question type: {question_type}""",
            context=""
        )
        
        # Step 3: Link documents based on question type
        if "bridge" in question_type.lower():
            linked_documents = await self.generate(
                instruction=f"""Identify documents sharing common entities or themes:
                - Entities: {entities_and_relationships}
                - Question Type: Bridge
                Find connections between documents.""",
                context=""
            )
        elif "comparison" in question_type.lower():
            linked_documents = await self.generate(
                instruction=f"""Identify documents containing comparable attributes:
                - Attributes: {entities_and_relationships}
                - Question Type: Comparison
                Find relevant comparisons.""",
                context=""
            )
        else:  # Compositional
            linked_documents = await self.generate(
                instruction=f"""Identify documents contributing to the overall answer:
                - Facts: {entities_and_relationships}
                - Question Type: Compositional
                Combine information logically.""",
                context=""
            )
        
        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain across documents:
            - Linked Documents: {linked_documents}
            - Entities and Relationships: {entities_and_relationships}
            Trace logical connections to derive the answer.""",
            context=linked_documents
        )
        
        # Step 5: Extract and validate answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Reasoning Chain: {reasoning_chain}
            Ensure the answer is factually correct and supported by evidence.""",
            context=reasoning_chain
        )
        
        # Step 6: Compile supporting facts
        supporting_facts = await self.generate(
            instruction=f"""Compile supporting facts for the answer:
            - Answer: {answer}
            - Reasoning Chain: {reasoning_chain}
            List exact sentences or phrases from the documents.""",
            context=reasoning_chain
        )
        
        # Final Output
        return {
            "question_type": question_type,
            "reasoning_chain": reasoning_chain,
            "answer": answer,
            "supporting_facts": supporting_facts
        }