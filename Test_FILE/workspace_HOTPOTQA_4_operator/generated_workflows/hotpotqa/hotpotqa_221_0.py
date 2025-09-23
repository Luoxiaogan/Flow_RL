# Workflow ID: hotpotqa_221_0
# Benchmark: hotpotqa
# Data Indices: [278, 418]

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
        
        # Initial Analysis: Classify the question type and identify relevant documents
        initial_analysis = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            1. Bridge Question: Connects information through shared entities (e.g., "What nationality is the director of [movie]?")
            2. Comparison Question: Compares properties across documents (e.g., "Which was founded first, X or Y?")
            3. Compositional Question: Combines multiple facts to derive an answer (e.g., "What American composer was recognized by a privately funded foundation that was conceived in 1978?")
            
            Also, identify which documents are likely to contain the necessary information.
            Provide structured classification and document relevance.""",
            context=""
        )
        
        # Entity Extraction: Extract named entities and relationships from each document
        entities_list = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all named entities and relationships from Document {i+1}:
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ) for i in range(10)]  # Assuming up to 10 documents
        )
        
        # Ensemble: Identify bridging entities that connect documents
        bridging_entities = await self.ensemble(
            instruction="""Identify bridging entities that connect multiple documents:
            - Shared entities (e.g., same person, organization, event)
            - Relationships that link documents logically
            Select the most plausible bridging entities based on contextual evidence.""",
            contexts_list=entities_list
        )
        
        # Reasoning Chain Construction: Build logical chain connecting entities to answer the question
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridging entities:
            {bridging_entities}
            
            Construct a logical reasoning chain that connects the entities to answer the question.
            Ensure the chain follows a coherent path from question to answer.""",
            context=initial_analysis
        )
        
        # Answer Extraction: Extract precise answer from the final document in the reasoning chain
        answer_extraction = await self.generate(
            instruction=f"""Based on the reasoning chain:
            {reasoning_chain}
            
            Extract the exact answer span from the final document.
            Ensure the answer is factually correct and directly addresses the question.""",
            context=reasoning_chain
        )
        
        # Validation and Refinement: Validate the extracted answer and refine if necessary
        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            {answer_extraction}
            
            Check against the original question and supporting facts.
            If discrepancies arise, refine the answer to ensure accuracy and coherence.""",
            context=answer_extraction
        )
        
        return validated_answer