# Workflow ID: hotpotqa_246_0
# Benchmark: hotpotqa
# Data Indices: [243, 238]

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
        
        # Step 1: Initial Analysis - Classify Question Type
        question_analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            - Bridge: Requires connecting entities across documents
            - Comparison: Involves comparing properties
            - Compositional: Combines multiple facts
            Provide structured classification and outline potential reasoning path.""",
            context=""
        )
        
        # Step 2: Parallel Entity Extraction from All Documents
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, numbers, and relationships from Document {i+1}.
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)
        
        # Step 3: Bridge Entity Identification via Ensemble Voting
        bridge_entity_identification = await self.ensemble(
            instruction="Identify shared entities across documents that serve as bridges.",
            contexts_list=extracted_entities
        )
        
        # Step 4: Reasoning Chain Construction - Iterative Process
        reasoning_chain = ""
        for _ in range(3):  # Limit iterations to prevent infinite loops
            reasoning_step = await self.generate(
                instruction=f"""Using the identified bridge entities: {bridge_entity_identification}
                Construct the next step in the reasoning chain by connecting documents.
                Validate each step with evidence from the documents.""",
                context=reasoning_chain
            )
            reasoning_chain += reasoning_step
            if "final answer" in reasoning_step.lower():
                break
        
        # Step 5: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""From the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span and identify supporting facts from different documents.
            Ensure the answer is factually correct and directly supported by evidence.""",
            context=""
        )
        
        refined_answer = await self.revise(
            instruction="Refine the extracted answer for clarity and precision.",
            context=answer_extraction
        )
        
        supporting_facts = await self.summarize(
            instruction="Condense the supporting facts into a concise format.",
            context=reasoning_chain
        )
        
        return {
            "answer": refined_answer,
            "supporting_facts": supporting_facts
        }