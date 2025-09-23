# Workflow ID: hotpotqa_36_0
# Benchmark: hotpotqa
# Data Indices: [121]

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
            instruction="""Classify this question as bridge, comparison, or compositional. 
            Provide reasoning for your choice. Focus on the structure and what the question is asking.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Based on the classification: {classification}
            Extract all named entities and relationships from the context documents. 
            Highlight entities that appear in multiple documents.""",
            context=classification
        )

        # Step 3: Build reasoning chains (parallel processing)
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted entities: {entities}
                Build a reasoning chain that connects Document 1 and Document 2. 
                Show how each document contributes to the final answer.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Using the extracted entities: {entities}
                Build a reasoning chain that connects Document 3 and other relevant documents. 
                Show how each document contributes to the final answer.""",
                context=entities
            )
        )

        # Step 4: Synthesize reasoning chains
        synthesis = await self.ensemble(
            instruction="Synthesize the reasoning chains into a unified understanding. Resolve any conflicts.",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract the precise answer
        answer = await self.generate(
            instruction=f"""From the synthesized reasoning chain: {synthesis}
            Extract the precise answer to the question. Ensure it is a short text span or a yes/no response.""",
            context=synthesis
        )

        # Optional Iterative Refinement
        refined_answer = await self.revise(
            instruction=f"""Review the extracted answer: {answer}
            Ensure it is factually correct, concise, and directly addresses the question. Make any necessary revisions.""",
            context=answer
        )

        return refined_answer