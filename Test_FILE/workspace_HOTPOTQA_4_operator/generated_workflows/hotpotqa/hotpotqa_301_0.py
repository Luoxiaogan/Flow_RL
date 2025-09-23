# Workflow ID: hotpotqa_301_0
# Benchmark: hotpotqa
# Data Indices: [457, 353]

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
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract all named entities, relationships, and constraints.
            3. Structure the output as:
               - Question Type: [type]
               - Entities: [list of entities]
               - Constraints: [list of constraints]""",
            context=""
        )
        
        # Parse analysis to determine question type
        question_type = "bridge" if "bridge" in analysis.lower() else "comparison" if "comparison" in analysis.lower() else "compositional"
        
        # Phase 2: Document Linking and Reasoning Chain Construction
        documents = self.problem_text.split("**QUESTION:**")[0].split("Document ")[1:]
        parallel_tasks = [
            self.generate(
                instruction=f"""Process Document {i}:
                1. Identify sentences containing entities: {analysis}.
                2. Highlight relationships and facts relevant to the question.
                3. Provide structured output.""",
                context=doc
            ) for i, doc in enumerate(documents, start=1)
        ]
        processed_docs = await asyncio.gather(*parallel_tasks)
        
        reasoning_chain = await self.ensemble(
            instruction=f"""Synthesize a reasoning chain:
            1. Identify connections between documents using entities: {analysis}.
            2. Build a logical sequence linking facts across documents.
            3. Highlight the 'bridge entity' or shared concept.""",
            contexts_list=processed_docs
        )
        
        # Phase 3: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer:
            1. Use the reasoning chain: {reasoning_chain}.
            2. Identify the exact answer span from the final document.
            3. Validate the answer against the original question.""",
            context=self.problem_text
        )
        
        refined_answer = await self.revise(
            instruction="Refine the answer for clarity and precision.",
            context=answer_extraction
        )
        
        summary = await self.summarize(
            instruction="Summarize the reasoning chain and supporting facts.",
            context=reasoning_chain
        )
        
        return {
            "answer": refined_answer.strip(),
            "reasoning": summary.strip()
        }