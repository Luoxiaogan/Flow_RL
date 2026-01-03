# Workflow ID: hotpotqa_73_0
# Benchmark: hotpotqa
# Data Indices: [33]

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
            instruction="""Classify the question into one of the following types:
            1. Bridge: Questions requiring connection through shared entities.
            2. Comparison: Questions comparing properties across documents.
            3. Compositional: Questions combining multiple facts.
            
            Provide a detailed explanation of why the question fits into this category and suggest initial strategies for solving it.""",
            context=""
        )
        
        # Step 2: Extract entities and identify bridge entities
        entities = await self.generate(
            instruction=f"""Based on the classification: {classification}
            
            Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            
            Identify potential bridge entities that connect different documents.""",
            context=classification
        )
        
        # Step 3: Build reasoning chains
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the entities: {entities}
                
                Create a reasoning chain that connects the information across documents to answer the question.
                Ensure each step is logically consistent and factually accurate.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Using the entities: {entities}
                
                Create an alternative reasoning chain that connects the information across documents to answer the question.
                Ensure each step is logically consistent and factually accurate.""",
                context=entities
            )
        )
        
        best_reasoning_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains and select the most plausible one:
            - Check factual accuracy against the provided documents.
            - Ensure logical consistency across the chain.
            - Select the chain that best answers the question.""",
            contexts_list=reasoning_paths
        )
        
        # Step 4: Extract and validate the answer
        answer_extraction = await self.generate(
            instruction=f"""From the reasoning chain: {best_reasoning_chain}
            
            Extract the precise answer to the question.
            Ensure the answer is a short, factual response directly extracted from the text.""",
            context=best_reasoning_chain
        )
        
        final_answer = await self.revise(
            instruction=f"""Validate the extracted answer: {answer_extraction}
            
            Ensure it is factually correct and directly addresses the question.
            If necessary, refine the answer to improve clarity and precision.""",
            context=answer_extraction
        )
        
        return final_answer