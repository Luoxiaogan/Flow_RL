# Workflow ID: hotpotqa_217_0
# Benchmark: hotpotqa
# Data Indices: [496, 145]

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
        
        # Step 1: Question Analysis
        question_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Highlight any bridge entities that connect documents.
            Provide structured output with clear labels.""",
            context=""
        )
        
        # Step 2: Document Mapping
        document_mapping = await self.generate(
            instruction=f"""Map entities to relevant documents:
            Question Analysis: {question_analysis}
            
            For each key entity:
            - Find documents mentioning the entity.
            - Identify sentences describing its relationships.
            Provide a list of relevant documents and their connection points.""",
            context=question_analysis
        )
        
        # Step 3: Reasoning Chain Construction (Parallel Exploration)
        reasoning_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain:
                Question Analysis: {question_analysis}
                Document Mapping: {document_mapping}
                
                Using the following hypothesis:
                Hypothesis {i+1}: [Describe hypothesis]
                
                Build a logical chain connecting documents through shared entities or relationships.
                Ensure each step is factually supported.""",
                context=document_mapping
            ) for i in range(3)]  # Explore 3 hypotheses in parallel
        )
        
        # Validate and refine reasoning paths
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the reasoning chain:
                Original Chain: {path}
                
                Check for:
                - Factual accuracy
                - Logical coherence
                - Completeness
                Revise as needed.""",
                context=path
            ) for path in reasoning_paths]
        )
        
        # Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction=f"""Evaluate reasoning chains:
            Chains: {refined_paths}
            
            Select the most plausible chain based on:
            - Strength of evidence
            - Logical consistency
            - Relevance to the question""",
            contexts_list=refined_paths
        )
        
        # Step 4: Answer Extraction
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer:
            Best Reasoning Chain: {best_chain}
            
            From the final document in the chain, extract:
            - The exact answer span (entity/phrase)
            - Ensure it matches the question requirements
            Avoid paraphrasing or summarization.""",
            context=best_chain
        )
        
        # Validate the extracted answer
        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            Extracted Answer: {answer_extraction}
            
            Check for:
            - Exact match to the question
            - Factual correctness
            - Proper format (short text span or yes/no)
            Revise if necessary.""",
            context=answer_extraction
        )
        
        # Step 5: Supporting Facts Identification
        supporting_facts = await self.generate(
            instruction=f"""Identify supporting facts:
            Best Reasoning Chain: {best_chain}
            
            Trace the reasoning chain back to specific sentences in specific documents.
            Provide supporting facts with:
            - Document titles
            - Sentence IDs
            - Relevant excerpts""",
            context=best_chain
        )
        
        return {
            "answer": validated_answer,
            "supporting_facts": supporting_facts
        }