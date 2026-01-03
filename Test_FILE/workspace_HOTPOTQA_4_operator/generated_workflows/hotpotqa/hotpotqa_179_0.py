# Workflow ID: hotpotqa_179_0
# Benchmark: hotpotqa
# Data Indices: [477]

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

        # Phase 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem to classify its type (bridge, comparison, compositional).
            Extract key entities and relationships mentioned in the question.
            Identify potential bridge entities that could connect documents.
            Provide structured output including:
            - Question type
            - Key entities
            - Potential bridge entities""",
            context=""
        )

        summary = await self.summarize(
            instruction="Condense the analysis into a structured format focusing on entities, question type, and bridge entities.",
            context=analysis
        )

        # Phase 2: Parallel Exploration
        bridge_entities, direct_evidence, constraints = await asyncio.gather(
            self.generate(
                instruction=f"Search for bridge entities connecting documents based on: {summary}",
                context=""
            ),
            self.generate(
                instruction=f"Identify direct evidence supporting the answer based on: {summary}",
                context=""
            ),
            self.generate(
                instruction=f"Evaluate constraints or conditions implied by the question based on: {summary}",
                context=""
            )
        )

        # Phase 3: Conditional Branching
        if "bridge" in summary.lower():
            reasoning_chain = await self.generate(
                instruction=f"Trace connections using bridge entities: {bridge_entities}. Build a reasoning chain.",
                context=summary
            )
        elif "comparison" in summary.lower():
            reasoning_chain = await self.generate(
                instruction=f"Compare properties across documents based on: {direct_evidence}. Build a reasoning chain.",
                context=summary
            )
        else:
            reasoning_chain = await self.generate(
                instruction=f"Combine multiple facts to derive the answer based on: {direct_evidence}. Build a reasoning chain.",
                context=summary
            )

        # Phase 4: Evidence Synthesis
        refined_chain = await self.revise(
            instruction="Refine the reasoning chain to ensure clarity and factual correctness.",
            context=reasoning_chain
        )

        synthesis = await self.ensemble(
            instruction="Merge insights from parallel paths into a unified reasoning chain.",
            contexts_list=[refined_chain, direct_evidence, constraints]
        )

        # Phase 5: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"Extract the precise answer span from the final document based on: {synthesis}.",
            context=synthesis
        )

        validated_answer = await self.revise(
            instruction="Validate the answer against the evidence chain and refine if necessary.",
            context=answer
        )

        return validated_answer