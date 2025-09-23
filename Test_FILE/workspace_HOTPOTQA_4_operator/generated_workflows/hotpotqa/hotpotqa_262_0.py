# Workflow ID: hotpotqa_262_0
# Benchmark: hotpotqa
# Data Indices: [1, 104]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Classify the question type (bridge, comparison, compositional).
            - Identify key entities, relationships, and constraints.
            - Highlight documents likely to contain relevant information.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Document Analysis
        documents = [f"Document {i+1}" for i in range(10)]  # Assuming up to 10 documents
        document_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract key facts from {doc}:
                - Focus on entities, dates, and relationships.
                - Highlight information relevant to the question.
                Format as bullet points.""",
                context=analysis
            ) for doc in documents]
        )

        # Step 3: Identify Bridge Entities
        bridge_entities = await self.ensemble(
            instruction="""Identify bridge entities connecting documents:
            - Look for shared entities, concepts, or relationships.
            - Prioritize entities mentioned in multiple documents.
            - Consider indirect connections through intermediate facts.
            Synthesize findings into a list of potential bridge entities.""",
            contexts_list=document_facts
        )

        # Step 4: Build Reasoning Chains
        reasoning_chains = await self.generate(
            instruction=f"""Using bridge entities: {bridge_entities}
            Construct reasoning chains that connect documents:
            - Follow logical relationships between facts.
            - Derive intermediate conclusions.
            - Ensure each step is supported by evidence.
            Present as a clear narrative.""",
            context=analysis
        )

        # Step 5: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"""Extract the final answer from the reasoning chains:
            - Use exact answer spans from the text.
            - Ensure the answer is factually correct and supported by evidence.
            - Format as a short, factual response.""",
            context=reasoning_chains
        )
        validated_answer = await self.revise(
            instruction="""Validate the answer:
            - Check for consistency with the evidence chain.
            - Refine wording if necessary.
            - Ensure precision and clarity.""",
            context=answer
        )

        # Step 6: Conditional Branching (Fallback Strategy)
        if "unclear" in validated_answer.lower() or "ambiguous" in validated_answer.lower():
            refined_analysis = await self.revise(
                instruction="Re-analyze the problem with alternative focus areas.",
                context=analysis
            )
            fallback_answer = await self.generate(
                instruction=f"""Attempt alternative reasoning path:
                - Explore new connections.
                - Use different documents or facts.
                - Derive a new answer.""",
                context=refined_analysis
            )
            return fallback_answer

        return validated_answer