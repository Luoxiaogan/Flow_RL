# Workflow ID: hotpotqa_33_0
# Benchmark: hotpotqa
# Data Indices: [485]

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
        
        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            - Is it a bridge question, comparison question, or compositional question?
            - Extract all key entities mentioned in the question.
            - Identify potential bridge entities that might connect documents.
            Provide structured output with clear labels.""",
            context=""
        )
        
        # Step 2: Parallel Hypothesis Generation - Explore multiple reasoning paths
        hypotheses = await asyncio.gather(
            *[self.generate(
                instruction=f"""For the bridge entity '{entity}', generate a hypothesis:
                - How does this entity connect the documents?
                - What reasoning chain can be constructed using this entity?
                Provide detailed reasoning steps.""",
                context=initial_analysis
            ) for entity in extract_entities(initial_analysis)]
        )
        
        # Step 3: Reasoning Chain Validation - Validate each hypothesis
        validated_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the reasoning chain for '{entity}':
                - Check for factual accuracy and consistency.
                - Ensure each step is supported by evidence from the documents.
                Revise the chain if necessary.""",
                context=hypothesis
            ) for entity, hypothesis in zip(extract_entities(initial_analysis), hypotheses)]
        )
        
        # Step 4: Ensemble Decision - Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Select the most plausible reasoning chain:
            - Criteria: Factual accuracy, completeness, alignment with the question.
            - Provide justification for the selection.""",
            contexts_list=validated_chains
        )
        
        # Step 5: Answer Extraction - Extract precise answer span
        answer = await self.generate(
            instruction=f"""From the selected reasoning chain:
            {best_chain}
            
            Extract the precise answer span that directly answers the question.
            Ensure the answer is verbatim from the documents and factually correct.""",
            context=best_chain
        )
        
        # Step 6: Final Validation - Validate the extracted answer
        final_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Ensure it matches the question.
            - Verify it is supported by the documents.
            Revise if necessary.""",
            context=answer
        )
        
        return final_answer

def extract_entities(text):
    """Helper function to extract entities from structured analysis."""
    # Placeholder implementation - replace with actual parsing logic
    return ["Entity1", "Entity2", "Entity3"]