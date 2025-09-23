# Workflow ID: hotpotqa_195_0
# Benchmark: hotpotqa
# Data Indices: [191]

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

        # Step 1: Initial Analysis - Identify problem type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Identify potential bridge entities that connect documents.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Entity Resolution - Resolve ambiguities in entity extraction
        entity_interpretations = await asyncio.gather(
            self.generate(instruction="Resolve entities assuming interpretation A.", context=initial_analysis),
            self.generate(instruction="Resolve entities assuming interpretation B.", context=initial_analysis),
            self.generate(instruction="Resolve entities assuming interpretation C.", context=initial_analysis)
        )
        resolved_entities = await self.ensemble(
            instruction="Select the most plausible entity interpretation based on coherence and factual support.",
            contexts_list=entity_interpretations
        )

        # Step 3: Reasoning Chain Construction - Build reasoning chain based on problem type
        reasoning_chain = await self.generate(
            instruction=f"""Construct reasoning chain:
            Problem type: {initial_analysis.split('
')[0]}
            Resolved entities: {resolved_entities}
            Follow logical connections across documents to build a coherent chain.
            Ensure each step is factually supported.""",
            context=resolved_entities
        )

        # Step 4: Iterative Refinement - Validate and refine reasoning chain
        refined_chain = reasoning_chain
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction="Validate reasoning chain for completeness and accuracy.",
                context=refined_chain
            )
            if "complete" in validation.lower() and "accurate" in validation.lower():
                break
            refined_chain = await self.revise(
                instruction=f"Address gaps/inconsistencies: {validation}",
                context=refined_chain
            )

        # Step 5: Final Answer Extraction - Extract precise answer and supporting facts
        final_answer = await self.generate(
            instruction=f"""Extract final answer:
            Reasoning chain: {refined_chain}
            Provide a short, factual answer directly addressing the question.
            Include supporting facts from the reasoning chain.""",
            context=refined_chain
        )

        return final_answer