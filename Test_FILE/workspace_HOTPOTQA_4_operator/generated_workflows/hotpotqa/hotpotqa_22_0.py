# Workflow ID: hotpotqa_22_0
# Benchmark: hotpotqa
# Data Indices: [109, 218]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities (people, places, organizations).
            3. Identify potential bridge entities connecting documents.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Document Filtering
        filtered_docs = await self.generate(
            instruction=f"""Using the extracted entities:
            {analysis}
            
            Filter relevant documents:
            - Identify documents containing key entities.
            - Prioritize documents with shared entities.
            Provide a ranked list of relevant documents.""",
            context=analysis
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Construct reasoning chain 1:
                Using entities and filtered documents:
                {filtered_docs}
                
                Build a logical path connecting facts across documents.""",
                context=filtered_docs
            ),
            self.generate(
                instruction=f"""Construct reasoning chain 2:
                Using entities and filtered documents:
                {filtered_docs}
                
                Explore alternative logical paths.""",
                context=filtered_docs
            )
        )

        # Phase 4: Answer Extraction
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract answer from reasoning chain 1:
                {reasoning_paths[0]}
                
                Identify the precise answer span from the final document.""",
                context=reasoning_paths[0]
            ),
            self.generate(
                instruction=f"""Extract answer from reasoning chain 2:
                {reasoning_paths[1]}
                
                Identify the precise answer span from the final document.""",
                context=reasoning_paths[1]
            )
        )

        # Phase 5: Validation and Refinement
        refined_answers = await asyncio.gather(
            self.revise(
                instruction="Improve clarity and verify factual correctness.",
                context=candidate_answers[0]
            ),
            self.revise(
                instruction="Improve clarity and verify factual correctness.",
                context=candidate_answers[1]
            )
        )

        # Final Synthesis
        final_answer = await self.ensemble(
            instruction="Select the most accurate and well-supported answer.",
            contexts_list=refined_answers
        )

        return final_answer