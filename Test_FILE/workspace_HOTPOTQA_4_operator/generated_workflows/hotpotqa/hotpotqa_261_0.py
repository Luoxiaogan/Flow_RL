# Workflow ID: hotpotqa_261_0
# Benchmark: hotpotqa
# Data Indices: [74, 210]

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

        # Initial Analysis: Classify the question type
        analysis = await self.generate(
            instruction="""Analyze the question to determine its type:
            1. Is it a bridge question requiring connection through shared entities?
            2. Is it a comparison question involving properties across documents?
            3. Is it a compositional question that combines multiple facts?
            Provide a structured classification with reasoning.""",
            context=""
        )

        # Parallel Document Processing: Extract relevant information
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_tasks = []
        for doc in documents.split("Document ")[1:]:
            title = doc.split("\n")[0].strip()
            content = "\n".join(doc.split("\n")[1:]).strip()
            doc_tasks.append(
                self.generate(
                    instruction=f"""Extract relevant information from the document titled '{title}':
                    - Identify entities mentioned in the question.
                    - Extract significant facts related to these entities.
                    - Note any indirect references or relationships.""",
                    context=content
                )
            )
        doc_results = await asyncio.gather(*doc_tasks)

        # Entity Linking and Reasoning Chain Construction
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from all documents:
            - Identify common entities across documents.
            - Construct a logical chain connecting these entities.
            - Highlight supporting facts that validate the connections.""",
            contexts_list=doc_results
        )

        # Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer from the final document in the chain.
            Ensure the answer is a short text span directly from the document.""",
            context=""
        )

        answer_validation = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Check for factual correctness.
            - Ensure consistency with the reasoning chain.
            - Confirm the answer matches the expected format.""",
            context=answer_extraction
        )

        # Final Output: Summarize the process and result
        final_output = await self.summarize(
            instruction=f"""Summarize the entire reasoning process and result:
            - Include the final answer.
            - List supporting facts from different documents.
            - Maintain clarity and conciseness.""",
            context=f"{analysis}

{reasoning_chain}

{answer_validation}"
        )

        return final_output