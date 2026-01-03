# Workflow ID: hotpotqa_208_0
# Benchmark: hotpotqa
# Data Indices: [347, 479]

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

        # Step 1: Analyze the problem and classify question type
        problem_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities and constraints mentioned in the question.
            3. List any implicit relationships or conditions.
            Provide structured output.""",
            context=""
        )

        # Step 2: Process documents in parallel to extract entities and facts
        document_contexts = []
        for i in range(1, 11):  # Assuming up to 10 documents
            doc_analysis = await self.generate(
                instruction=f"""Extract entities, relationships, and key facts from Document {i}.
                Focus on information relevant to the question constraints.
                Format as structured list.""",
                context=problem_analysis
            )
            document_contexts.append(doc_analysis)

        # Step 3: Identify bridge entities across documents
        bridge_entities = await self.ensemble(
            instruction="""Compare entities across documents:
            1. Identify shared entities or concepts that connect documents.
            2. Highlight relationships that satisfy the question constraints.
            Select the most plausible bridge entities.""",
            contexts_list=document_contexts
        )

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities:
            {bridge_entities}
            
            Construct a logical reasoning chain:
            - Start with the question constraints.
            - Connect documents step-by-step through bridge entities.
            - Ensure each link is supported by evidence.
            Provide detailed chain.""",
            context=problem_analysis
        )

        # Step 5: Extract precise answer
        answer = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the final document.
            Ensure the answer matches the expected format (short text span, yes/no).""",
            context=problem_analysis
        )

        # Step 6: Compile supporting evidence
        evidence_summary = await self.summarize(
            instruction=f"""Summarize supporting facts from the reasoning chain:
            {reasoning_chain}
            
            Preserve key details while reducing verbosity.
            Ensure all supporting facts are factually accurate.""",
            context=reasoning_chain
        )

        return {
            "answer": answer,
            "supporting_facts": evidence_summary
        }