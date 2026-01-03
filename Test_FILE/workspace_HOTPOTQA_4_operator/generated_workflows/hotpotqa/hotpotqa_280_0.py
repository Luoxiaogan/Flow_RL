# Workflow ID: hotpotqa_280_0
# Benchmark: hotpotqa
# Data Indices: [401, 429]

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
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key entities and relationships
            - Determine the type of question (bridge, comparison, compositional)
            - Extract constraints and conditions
            Provide structured analysis.""",
            context=""
        )
        
        # Step 2: Identify Bridge Entities
        bridge_entities = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Identify bridge entities that connect the documents:
            - Extract entities from the question
            - Find their mentions in the documents
            Provide a list of bridge entities and their connections.""",
            context=initial_analysis
        )
        
        # Step 3: Build Reasoning Chain
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""For each bridge entity:
                {entity}
                
                Generate hypotheses about how they connect the documents:
                - Describe the relationship
                - Identify supporting facts
                - Refine the hypothesis""",
                context=bridge_entities
            ) for entity in bridge_entities.split('\n')]
        )
        
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the reasoning chain:
                {chain}
                
                Improve clarity and add specific details
                Ensure logical consistency""",
                context=chain
            ) for chain in reasoning_chains]
        )
        
        # Step 4: Extract Precise Answer
        summarized_answers = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Summarize the reasoning chain:
                {chain}
                
                Extract the precise answer span:
                - Ensure factual correctness
                - Provide short, concise answer""",
                context=chain
            ) for chain in refined_chains]
        )
        
        final_answer = await self.ensemble(
            instruction="""Synthesize all summarized answers into a single final answer:
            - Select the most factually correct answer
            - Ensure it is concise and supported by evidence""",
            contexts_list=summarized_answers
        )
        
        # Step 5: Return Final Answer
        return final_answer