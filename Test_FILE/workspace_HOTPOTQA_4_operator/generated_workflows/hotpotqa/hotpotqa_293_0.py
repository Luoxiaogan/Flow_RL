# Workflow ID: hotpotqa_293_0
# Benchmark: hotpotqa
# Data Indices: [462, 168]

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

        # Step 1: Initial Analysis - Classify question type and extract entities/relationships
        initial_analysis = await self.generate(
            instruction="""Classify the question type and extract key information:
            1. Is it a bridge, comparison, or compositional question?
            2. Extract all named entities, numbers, and relationships.
            3. Identify potential bridge entities that connect documents.
            Format the output as structured JSON.""",
            context=""
        )

        # Step 2: Parallel Processing - Build reasoning chains for each question type
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""For bridge questions, connect shared entities across documents:
                Question: {self.problem_text}
                Entities: {initial_analysis}
                Build reasoning chains that link documents through shared entities.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""For comparison questions, evaluate properties across documents:
                Question: {self.problem_text}
                Entities: {initial_analysis}
                Compare properties and build reasoning chains.""",
                context=initial_analysis
            )
        )

        # Step 3: Refinement - Iteratively refine reasoning chains
        refined_chains = []
        for chain in reasoning_chains:
            refined = await self.revise(
                instruction=f"""Refine the reasoning chain:
                Original Chain: {chain}
                Add missing details, correct logical gaps, and validate against context documents.""",
                context=chain
            )
            refined_chains.append(refined)

        # Step 4: Answer Extraction - Summarize and select the best answer
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Summarize the reasoning chain:
                Chain: {chain}
                Extract the precise answer and supporting facts.""",
                context=chain
            ) for chain in refined_chains]
        )
        final_answer = await self.ensemble(
            instruction="Select the best candidate answer based on completeness and accuracy.",
            contexts_list=summaries
        )

        # Step 5: Supporting Facts Identification
        supporting_facts = await self.generate(
            instruction=f"""Extract supporting facts from context documents:
            Reasoning Chain: {final_answer}
            Identify sentences or phrases that support the answer.""",
            context=final_answer
        )

        return {
            "answer": final_answer,
            "supporting_facts": supporting_facts
        }