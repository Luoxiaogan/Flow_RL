# Workflow ID: hotpotqa_182_0
# Benchmark: hotpotqa
# Data Indices: [260, 79]

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
            instruction="""Analyze the question:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities and their relationships.
            3. Highlight potential bridge entities connecting documents.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Exploration - Extract relevant information from all documents
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_titles = [line.split(":")[0].strip() for line in documents.split("\n") if line.startswith("Document")]
        parallel_tasks = [
            self.generate(
                instruction=f"""Extract information from '{doc}':
                1. Identify mentions of key entities from the question.
                2. Highlight relevant facts and relationships.
                3. Focus on information that could connect to other documents.
                Provide concise summary.""",
                context=initial_analysis
            ) for doc in doc_titles
        ]
        extracted_info = await asyncio.gather(*parallel_tasks)

        # Step 3: Reasoning Chain Construction - Build connections between entities and documents
        reasoning_chain = await self.generate(
            instruction=f"""Using extracted information:
            {extracted_info}
            
            Construct a reasoning chain:
            1. Identify bridge entities connecting documents.
            2. Follow logical connections to build a path from question to answer.
            3. Highlight supporting facts from different documents.
            Provide step-by-step reasoning.""",
            context=initial_analysis
        )

        # Step 4: Iterative Refinement - Resolve ambiguities and conflicting information
        refined_chain = reasoning_chain
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                {refined_chain}
                
                Check for:
                1. Ambiguities in entity references.
                2. Conflicting information from different documents.
                3. Missing links in the reasoning chain.
                Provide detailed feedback.""",
                context=refined_chain
            )
            if "error" in validation.lower() or "conflict" in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"""Refine the reasoning chain based on feedback:
                    {validation}
                    
                    Ensure clarity, consistency, and completeness.""",
                    context=refined_chain
                )
            else:
                break

        # Step 5: Answer Extraction - Extract precise answer span from final document
        answer = await self.generate(
            instruction=f"""Using the refined reasoning chain:
            {refined_chain}
            
            Extract the precise answer:
            1. Identify the final document containing the answer.
            2. Locate the exact answer span (entity/phrase).
            3. Ensure the answer is factually correct and supported by evidence.
            Provide short, factual answer.""",
            context=refined_chain
        )

        # Step 6: Ensemble Resolution - Handle conflicting answers (if any)
        final_answer = await self.ensemble(
            instruction="""Synthesize all available information:
            1. Resolve any remaining conflicts.
            2. Select the most consistent and supported answer.
            3. Ensure the final output matches the required format.""",
            contexts_list=[answer, refined_chain]
        )

        return final_answer