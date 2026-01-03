# Workflow ID: hotpotqa_153_0
# Benchmark: hotpotqa
# Data Indices: [397, 214]

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
        question_type_analysis = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge: Requires connecting documents through shared entities.
            2. Comparison: Requires comparing properties across documents.
            3. Compositional: Requires combining multiple facts.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entity_extraction_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            entity_extraction_tasks.append(
                self.generate(
                    instruction=f"""Extract all named entities and relationships from Document {i}.
                    Format as a structured list with categories:
                    - People: [names and roles]
                    - Places: [locations and contexts]
                    - Numbers: [values and what they represent]
                    - Actions: [what happens and when]""",
                    context=""
                )
            )
        entities_list = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Identify bridge entities and construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities:
            {entities_list}
            
            Identify the bridge entity that connects the documents.
            Construct a reasoning chain that explains how the entities relate to each other
            and how they contribute to answering the question.""",
            context=question_type_analysis
        )

        # Step 4: Refine reasoning chain iteratively
        for _ in range(3):  # Limit iterations to balance depth and efficiency
            refined_chain = await self.revise(
                instruction="Refine the reasoning chain for clarity and completeness.",
                context=reasoning_chain
            )
            reasoning_chain = refined_chain

        # Step 5: Extract precise answer
        answer_extraction = await self.summarize(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer from the relevant document.
            Ensure the answer is factual, concise, and directly addresses the question.""",
            context=reasoning_chain
        )

        # Step 6: Identify supporting facts
        supporting_facts = await self.ensemble(
            instruction="Identify the supporting facts from different documents that validate the reasoning chain.",
            contexts_list=entities_list
        )

        # Final Output
        return {
            "answer": answer_extraction,
            "supporting_facts": supporting_facts
        }