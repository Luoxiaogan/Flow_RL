# Workflow ID: hotpotqa_285_0
# Benchmark: hotpotqa
# Data Indices: [92, 188]

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

        # Initial Analysis
        classification = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional).
            Extract key entities and relationships mentioned in the question.
            Identify potential bridge entities that connect different documents.""",
            context=""
        )

        # Document Processing
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document ")[1:]
        document_tasks = []
        for doc in documents:
            title = doc.split("\n")[0].strip()
            content = "\n".join(doc.split("\n")[1:]).strip()
            task = self.generate(
                instruction=f"""Extract relevant information from the document titled '{title}' related to the identified entities and relationships.
                Focus on information that helps answer the question: {classification}""",
                context=content
            )
            document_tasks.append(task)
        document_results = await asyncio.gather(*document_tasks)

        # Reasoning Chain Construction
        reasoning_chain = await self.ensemble(
            instruction="Synthesize information from different documents and build the reasoning chain.",
            contexts_list=document_results
        )

        # Answer Extraction
        raw_answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain.
            Ensure the answer is factually correct based on the provided documents.
            Reasoning chain: {reasoning_chain}""",
            context=""
        )

        refined_answer = await self.revise(
            instruction="Validate the extracted answer against the supporting facts and refine if necessary.",
            context=raw_answer
        )

        # Final Synthesis
        final_summary = await self.summarize(
            instruction="Condense the entire reasoning process into a concise summary.",
            context=f"{classification}\n{reasoning_chain}\n{refined_answer}"
        )

        return {
            "answer": refined_answer.strip(),
            "supporting_facts": final_summary.strip()
        }