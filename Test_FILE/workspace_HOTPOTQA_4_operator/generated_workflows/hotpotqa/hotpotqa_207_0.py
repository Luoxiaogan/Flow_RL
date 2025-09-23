# Workflow ID: hotpotqa_207_0
# Benchmark: hotpotqa
# Data Indices: [390, 350]

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
        
        # Step 1: Classify the question type and extract key entities
        classification = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and extract key entities (e.g., people, places, events). 
            Provide structured output: 
            - Question Type: [type]
            - Entities: [list of entities]""",
            context=""
        )
        
        # Step 2: Generate reasoning paths for each entity
        entities = classification.split("Entities:")[-1].strip().split(", ")
        reasoning_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"""For entity '{entity}', find relevant documents and extract facts. 
                Build a partial reasoning chain connecting this entity to the question.""",
                context=classification
            ) for entity in entities]
        )
        
        # Step 3: Synthesize reasoning chains
        synthesis = await self.ensemble(
            instruction="""Evaluate the reasoning chains and synthesize a coherent answer. 
            Prioritize chains supported by multiple documents and resolve contradictions.""",
            contexts_list=reasoning_paths
        )
        
        # Step 4: Validate and refine the answer
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction="""Critique the answer for factual accuracy and logical consistency. 
                Identify gaps or contradictions and suggest improvements.""",
                context=synthesis
            )
            if "error" not in validation.lower() and "gap" not in validation.lower():
                break
            synthesis = await self.revise(
                instruction=f"""Refine the answer based on critique: {validation}""",
                context=synthesis
            )
        
        # Step 5: Summarize the final answer
        final_answer = await self.summarize(
            instruction="""Condense the reasoning chain and present the final answer 
            in a concise format (short text span or yes/no response).""",
            context=synthesis
        )
        
        return final_answer