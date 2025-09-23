# Workflow ID: hotpotqa_176_0
# Benchmark: hotpotqa
# Data Indices: [86]

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
        
        # Step 1: Initial Analysis - Classify question type and extract high-level entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Identify main entities (people, places, organizations).
            - Highlight relationships between entities.
            Provide structured output.""",
            context=""
        )
        
        # Step 2: Parallel Entity Extraction - Extract entities and relationships from all documents
        entities_per_doc = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all entities and relationships from this document:
                - Entities: People, places, organizations, etc.
                - Relationships: How entities are connected.
                Format as structured list.""",
                context=doc
            ) for doc in self.extract_documents()]
        )
        
        # Step 3: Merge and Deduplicate Entities
        merged_entities = await self.ensemble(
            instruction="""Merge and deduplicate entities from all documents:
            - Prioritize entities most relevant to the question.
            - Remove duplicates and irrelevant entries.
            Provide consolidated list.""",
            contexts_list=entities_per_doc
        )
        
        # Step 4: Reasoning Chain Construction - Build logical connections
        reasoning_chain = await self.generate(
            instruction=f"""Using the following entities and relationships:
            {merged_entities}
            
            Construct a reasoning chain to answer the question:
            - Identify shared entities across documents.
            - Trace connections between entities.
            - Ensure the chain is logically consistent.
            Provide detailed reasoning steps.""",
            context=initial_analysis
        )
        
        # Step 5: Answer Extraction and Validation - Iterative refinement
        answer = ""
        for _ in range(3):  # Limit iterations to avoid infinite loops
            potential_answer = await self.generate(
                instruction=f"""Extract the precise answer from the reasoning chain:
                {reasoning_chain}
                
                Ensure the answer is:
                - Factually correct based on the documents.
                - In the required format (short text span or yes/no).
                Provide the answer and supporting facts.""",
                context=reasoning_chain
            )
            
            validation = await self.revise(
                instruction=f"""Validate the answer:
                - Check factual accuracy against documents.
                - Verify supporting facts are relevant.
                - Highlight any issues or ambiguities.
                Provide feedback.""",
                context=potential_answer
            )
            
            if "correct" in validation.lower() and "no issues" in validation.lower():
                answer = potential_answer
                break
            else:
                reasoning_chain = await self.revise(
                    instruction=f"""Refine the reasoning chain based on validation feedback:
                    {validation}
                    
                    Address issues and strengthen logical connections.""",
                    context=reasoning_chain
                )
        
        # Step 6: Final Synthesis - Summarize reasoning and return answer
        final_output = await self.summarize(
            instruction=f"""Summarize the reasoning chain and supporting facts:
            {reasoning_chain}
            
            Provide a concise explanation and the final answer.""",
            context=answer
        )
        
        return final_output
    
    def extract_documents(self):
        """Helper method to extract individual documents from the problem text."""
        sections = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        return [section.strip() for section in sections if section.strip()]