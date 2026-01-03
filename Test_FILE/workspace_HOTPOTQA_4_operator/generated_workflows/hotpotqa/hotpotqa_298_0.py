# Workflow ID: hotpotqa_298_0
# Benchmark: hotpotqa
# Data Indices: [344]

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
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining multiple facts)?
            Provide a clear classification.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        entities = await self.generate(
            instruction=f"""Extract key entities and relationships from the documents:
            - Identify people, places, organizations, and their attributes.
            - Highlight shared entities that could act as bridges.
            - Format as a structured list.""",
            context=""
        )

        # Step 3: Analyze documents in parallel
        document_analysis_tasks = []
        for i in range(10):  # Assuming up to 10 documents
            document_analysis_tasks.append(
                self.generate(
                    instruction=f"""Analyze Document {i+1}:
                    - Identify key facts relevant to the question.
                    - Highlight connections to other documents.
                    - Focus on entities and relationships.""",
                    context=entities
                )
            )
        document_analyses = await asyncio.gather(*document_analysis_tasks)

        # Step 4: Construct reasoning chains
        reasoning_chains = await self.generate(
            instruction=f"""Using the extracted entities and document analyses:
            - Build reasoning chains that connect the question to potential answers.
            - Ensure each chain is logically consistent and supported by evidence.
            - Prioritize chains that involve bridge entities.""",
            context="\n".join(document_analyses)
        )

        # Step 5: Extract and validate the final answer
        final_answer = await self.revise(
            instruction=f"""Extract the final answer from the reasoning chains:
            - Ensure the answer is a short, factual span from the text.
            - Validate against supporting facts from the documents.
            - If ambiguous, suggest refinements.""",
            context=reasoning_chains
        )

        # Step 6: Handle edge cases (if needed)
        if "ambiguous" in final_answer.lower() or "unclear" in final_answer.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on additional context:
                - Resolve ambiguities by revisiting earlier steps.
                - Generate alternative reasoning chains if necessary.""",
                context=final_answer
            )
            return refined_answer

        return final_answer