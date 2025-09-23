# Workflow ID: hotpotqa_102_0
# Benchmark: hotpotqa
# Data Indices: [229, 89]

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
        
        # Initial analysis to classify the question type
        analysis = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. Identify key entities and relationships.
            3. Determine the expected answer format.
            Provide structured classification.""",
            context=""
        )
        
        # Extract entities and relationships from documents
        entities = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Based on analysis: {analysis}""",
            context=""
        )
        
        # Build reasoning chains across documents
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Build reasoning chains for bridge entities:
                - Identify shared entities between documents
                - Follow connections to derive potential answers
                Based on entities: {entities}""",
                context=""
            ),
            self.generate(
                instruction=f"""Build reasoning chains for comparison:
                - Compare properties across documents
                - Identify differences and similarities
                Based on entities: {entities}""",
                context=""
            ),
            self.generate(
                instruction=f"""Build reasoning chains for composition:
                - Combine multiple facts to derive answers
                - Ensure logical consistency
                Based on entities: {entities}""",
                context=""
            )
        )
        
        # Synthesize reasoning chains into a unified understanding
        synthesis = await self.ensemble(
            instruction="Synthesize all reasoning chains into a unified understanding",
            contexts_list=reasoning_chains
        )
        
        # Extract and validate the final answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the final document:
            - Ensure factual correctness
            - Validate against reasoning chain
            Based on synthesis: {synthesis}""",
            context=""
        )
        
        final_answer = await self.revise(
            instruction="Refine and validate the extracted answer for clarity and correctness",
            context=answer_extraction
        )
        
        return final_answer