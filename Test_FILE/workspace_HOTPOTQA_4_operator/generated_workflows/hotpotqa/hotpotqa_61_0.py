# Workflow ID: hotpotqa_61_0
# Benchmark: hotpotqa
# Data Indices: [162]

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
            instruction="""Analyze the problem to classify the question type and extract key entities:
            - Classify as bridge, comparison, or compositional question
            - Extract named entities (people, places, concepts)
            - Identify potential bridge entities
            Provide structured output.""",
            context=""
        )
        
        # Step 2: Entity Linking and Reasoning Chain Construction
        entities = await self.generate(
            instruction=f"""Extract all entities and relationships from the documents:
            Entities: {initial_analysis}
            
            Format as structured list:
            - Document Title: [Entities]
            - Relationships: [Connections]""",
            context=initial_analysis
        )
        
        # Parallel processing for each document
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Build reasoning chain using entities:
                Entities: {entities}
                
                Connect entities across documents to form a chain.""",
                context=doc
            ) for doc in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document")]
        )
        
        # Merge reasoning chains
        merged_chain = await self.ensemble(
            instruction="Merge reasoning chains into a coherent path.",
            contexts_list=reasoning_chains
        )
        
        # Step 3: Answer Validation and Refinement
        refined_chain = await self.revise(
            instruction="Validate and refine the reasoning chain for accuracy and completeness.",
            context=merged_chain
        )
        
        # Step 4: Final Answer Extraction
        final_answer = await self.summarize(
            instruction=f"""Extract the precise answer span and supporting facts:
            Reasoning Chain: {refined_chain}
            
            Provide short factual answer with supporting evidence.""",
            context=refined_chain
        )
        
        return final_answer