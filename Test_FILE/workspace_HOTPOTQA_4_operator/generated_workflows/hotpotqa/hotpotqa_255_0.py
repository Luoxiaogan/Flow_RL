# Workflow ID: hotpotqa_255_0
# Benchmark: hotpotqa
# Data Indices: [56]

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
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge: Requires connecting documents through shared entities.
            2. Comparison: Requires comparing properties across documents.
            3. Compositional: Requires combining multiple facts to derive an answer.
            Provide the classification and explain your reasoning.""",
            context=""
        )
        
        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities and relationships from the documents:
            - Focus on entities relevant to the question type: {question_type}
            - Format as structured list with categories:
              * People/Organizations: [names and roles]
              * Places: [locations and contexts]
              * Numbers: [values and what they represent]
              * Actions: [what happens and when]""",
            context=question_type
        )
        
        # Step 3: Analyze each document independently
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_analysis_tasks = []
        for doc in documents.split("Document ")[1:]:
            title = doc.split("\n")[0].strip()
            content = "\n".join(doc.split("\n")[1:]).strip()
            task = self.generate(
                instruction=f"""Analyze this document:
                Title: {title}
                Content: {content}
                
                Extract facts relevant to the question type: {question_type}
                Focus on entities: {entities}""",
                context=entities
            )
            doc_analysis_tasks.append(task)
        
        doc_facts = await asyncio.gather(*doc_analysis_tasks)
        
        # Step 4: Synthesize reasoning chain
        reasoning_chain = await self.ensemble(
            instruction=f"""Synthesize a reasoning chain across documents:
            Question type: {question_type}
            Extracted entities: {entities}
            
            Combine facts from different documents to answer the question.
            Ensure the chain connects all relevant entities and relationships.""",
            contexts_list=doc_facts
        )
        
        # Step 5: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning chain: {reasoning_chain}
            
            Ensure the answer is factually correct and matches the required format (short text span or yes/no).""",
            context=reasoning_chain
        )
        
        validated_answer = await self.revise(
            instruction=f"""Validate the answer against the documents:
            Answer: {answer}
            
            Check for factual correctness and refine if necessary.""",
            context=answer
        )
        
        return validated_answer