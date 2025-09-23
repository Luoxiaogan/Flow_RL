# Workflow ID: hotpotqa_254_0
# Benchmark: hotpotqa
# Data Indices: [77]

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
        
        # Phase 1: Problem Analysis and Entity Extraction
        analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and extract key entities and relationships. Focus on:
            - Entities mentioned in the question
            - Shared entities across documents
            - Potential bridging entities""",
            context=""
        )
        
        # Parallel extraction of entities from all documents
        document_entities = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract all named entities and relationships from this document.",
                context=doc
            ) for doc in self.extract_documents()]
        )
        
        # Ensemble to unify entities
        unified_entities = await self.ensemble(
            instruction="Combine extracted entities into a unified set. Resolve duplicates and ambiguities.",
            contexts_list=document_entities
        )
        
        # Phase 2: Reasoning Chain Construction
        reasoning_chain = ""
        if "bridge" in analysis.lower():
            reasoning_chain = await self.build_bridge_reasoning(unified_entities)
        elif "comparison" in analysis.lower():
            reasoning_chain = await self.build_comparison_reasoning(unified_entities)
        else:
            reasoning_chain = await self.build_general_reasoning(unified_entities)
        
        # Validate reasoning chain
        validated_chain = await self.revise(
            instruction="Validate each step of the reasoning chain against the documents. Correct errors.",
            context=reasoning_chain
        )
        
        # Phase 3: Answer Extraction and Validation
        summary = await self.summarize(
            instruction="Condense the reasoning chain into a concise explanation.",
            context=validated_chain
        )
        
        answer = await self.generate(
            instruction=f"Extract the precise answer span from the final document. Ensure it matches the question: {self.extract_question()}",
            context=summary
        )
        
        final_answer = await self.revise(
            instruction="Validate the answer against the original question and supporting facts. Ensure factual correctness.",
            context=answer
        )
        
        return final_answer
    
    def extract_documents(self):
        """Extract individual document texts from the problem."""
        # Placeholder for document extraction logic
        pass
    
    def extract_question(self):
        """Extract the question text from the problem."""
        # Placeholder for question extraction logic
        pass
    
    async def build_bridge_reasoning(self, entities):
        """Construct reasoning chain for bridge questions."""
        return await self.generate(
            instruction=f"Connect shared entities across documents using: {entities}. Build a logical chain.",
            context=""
        )
    
    async def build_comparison_reasoning(self, entities):
        """Construct reasoning chain for comparison questions."""
        return await self.generate(
            instruction=f"Compare properties across documents using: {entities}. Highlight differences.",
            context=""
        )
    
    async def build_general_reasoning(self, entities):
        """Construct reasoning chain for general questions."""
        return await self.generate(
            instruction=f"Combine facts across documents using: {entities}. Derive a comprehensive answer.",
            context=""
        )