# Workflow ID: hotpotqa_97_0
# Benchmark: hotpotqa
# Data Indices: [340, 78]

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
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and extract key entities, relationships, and constraints. Format as:
            - Question Type: [type]
            - Entities: [list of entities]
            - Relationships: [list of relationships]""",
            context=""
        )

        # Step 2: Parallel Document Exploration - Analyze each document for relevant information
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_list = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        parallel_tasks = [
            self.generate(
                instruction=f"""Analyze this document for information related to entities: {initial_analysis}.
                Focus on sentences mentioning key entities and their relationships.""",
                context=doc
            ) for doc in doc_list
        ]
        doc_analyses = await asyncio.gather(*parallel_tasks)

        # Step 3: Reasoning Chain Construction - Combine insights into a coherent chain
        reasoning_chain = await self.ensemble(
            instruction="""Combine insights from the document analyses into a coherent reasoning chain.
            Trace logical dependencies and connect shared entities.""",
            contexts_list=doc_analyses
        )

        # Step 4: Answer Extraction and Validation - Extract precise answer and validate
        answer_extraction = await self.generate(
            instruction=f"""Based on the reasoning chain: {reasoning_chain},
            extract the precise answer to the question. Ensure it matches the expected format.""",
            context=""
        )
        validation = await self.revise(
            instruction=f"""Validate the answer: {answer_extraction} against the supporting facts.
            Ensure factual correctness and precision.""",
            context=reasoning_chain
        )

        # Step 5: Iterative Refinement (if needed)
        if "inconsistent" in validation.lower():
            refined_reasoning = await self.revise(
                instruction=f"""Refine the reasoning chain: {reasoning_chain}
                to resolve inconsistencies identified in validation: {validation}.""",
                context=reasoning_chain
            )
            refined_answer = await self.generate(
                instruction=f"""Extract the refined answer based on: {refined_reasoning}.""",
                context=""
            )
            return refined_answer
        else:
            return answer_extraction