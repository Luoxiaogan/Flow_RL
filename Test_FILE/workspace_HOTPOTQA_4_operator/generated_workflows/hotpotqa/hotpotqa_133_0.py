# Workflow ID: hotpotqa_133_0
# Benchmark: hotpotqa
# Data Indices: [85]

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

        # Step 1: Initial Analysis - Classify question type and extract bridge entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract potential bridge entities that connect documents.
            3. List all named entities and their relationships.""",
            context=""
        )

        # Step 2: Document-Specific Analysis - Analyze each document independently
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        document_tasks = []
        for doc in documents[1:]:
            title, content = doc.split("\n", 1)
            task = self.generate(
                instruction=f"""Extract structured information from this document:
                Title: {title.strip()}
                Content: {content.strip()}
                
                - Identify key entities and relationships.
                - Highlight facts relevant to the question.""",
                context=initial_analysis
            )
            document_tasks.append(task)
        document_analyses = await asyncio.gather(*document_tasks)

        # Step 3: Synthesis - Connect facts across documents
        synthesis = await self.ensemble(
            instruction="""Identify the most promising connections between documents:
            - Use bridge entities to link facts.
            - Construct explicit reasoning chains.
            - Prioritize high-confidence connections.""",
            contexts_list=document_analyses
        )

        # Step 4: Answer Refinement - Extract precise answer span
        refined_answer = await self.revise(
            instruction="""Refine the candidate answer:
            - Ensure it is factually correct and directly extracted from the text.
            - Validate against the reasoning chain.
            - Format as a short text span or yes/no response.""",
            context=synthesis
        )

        # Step 5: Iterative Validation - Handle ambiguity and ensure robustness
        for _ in range(3):  # Limit retries to prevent infinite loops
            validation = await self.generate(
                instruction=f"""Validate the answer:
                - Is it supported by the evidence chain?
                - Are there any ambiguities or gaps?""",
                context=refined_answer
            )
            if "error" in validation.lower() or "ambiguous" in validation.lower():
                refined_answer = await self.revise(
                    instruction=f"""Address issues identified in validation:
                    - Explore alternative bridge entities.
                    - Refine the reasoning chain.""",
                    context=refined_answer
                )
            else:
                break

        return refined_answer