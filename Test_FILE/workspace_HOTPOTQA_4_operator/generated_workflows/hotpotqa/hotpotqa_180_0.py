# Workflow ID: hotpotqa_180_0
# Benchmark: hotpotqa
# Data Indices: [144, 440]

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
            instruction="""Classify the question type and extract key components:
            1. Is it a bridge, comparison, or compositional question?
            2. Identify potential bridge entities or comparison anchors.
            3. List all named entities, relationships, and constraints.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Entity Exploration
        entities, relationships, constraints = await asyncio.gather(
            self.generate(
                instruction="Extract all named entities (people, places, films, etc.) from the documents.",
                context=analysis
            ),
            self.generate(
                instruction="Identify relationships between entities mentioned in the documents.",
                context=analysis
            ),
            self.generate(
                instruction="List any constraints or conditions stated in the documents.",
                context=analysis
            )
        )

        # Step 3: Conditional Branching
        if "bridge" in analysis.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Find shared entities between documents:
                Entities: {entities}
                Relationships: {relationships}
                Construct a reasoning chain connecting these entities.""",
                context=analysis
            )
        elif "comparison" in analysis.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Compare properties across documents:
                Entities: {entities}
                Constraints: {constraints}
                Evaluate which entity satisfies the comparison criteria.""",
                context=analysis
            )
        else:
            reasoning_chain = await self.generate(
                instruction=f"""Combine multiple facts to derive the answer:
                Entities: {entities}
                Relationships: {relationships}
                Constraints: {constraints}
                Build a compositional reasoning chain.""",
                context=analysis
            )

        # Step 4: Iterative Refinement
        refined_chain = reasoning_chain
        for _ in range(2):  # Limit iterations to avoid infinite loops
            refined_chain = await self.revise(
                instruction="Improve clarity and accuracy of the reasoning chain. Add missing details or fix logical gaps.",
                context=refined_chain
            )

        # Step 5: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document:
            Reasoning Chain: {refined_chain}
            Ensure the answer is a short text span or yes/no response.""",
            context=refined_chain
        )

        # Step 6: Evidence Gathering and Validation
        supporting_facts = await self.generate(
            instruction=f"""Collect supporting facts from different documents:
            Answer: {answer}
            Reasoning Chain: {refined_chain}
            Identify sentences that validate the answer.""",
            context=refined_chain
        )

        validated_answer = await self.ensemble(
            instruction=f"""Validate the answer against supporting facts:
            Answer: {answer}
            Supporting Facts: {supporting_facts}
            Ensure factual correctness and alignment with evidence.""",
            contexts_list=[answer, supporting_facts]
        )

        return validated_answer