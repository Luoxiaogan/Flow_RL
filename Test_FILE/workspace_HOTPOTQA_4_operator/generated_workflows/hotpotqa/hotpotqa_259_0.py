# Workflow ID: hotpotqa_259_0
# Benchmark: hotpotqa
# Data Indices: [177, 279]

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

        # Step 1: Classify the question type and extract key entities
        analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (chaining facts)?
            Also, extract all relevant entities and their relationships.
            Format the output as:
            Question Type: [type]
            Entities: [list of entities]""",
            context=""
        )

        # Step 2: Extract reasoning paths in parallel
        entities = [line.split(":")[1].strip() for line in analysis.split("\n") if "Entities" in line][0]
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using entity {entity}, find a reasoning path that connects documents.
                Identify the bridge entity and follow the chain of facts.""",
                context=analysis
            ) for entity in entities.split(", ")
        )

        # Step 3: Select the most plausible reasoning chain
        selected_path = await self.ensemble(
            instruction="""Evaluate the reasoning paths and select the most plausible one.
            Criteria:
            - Logical consistency
            - Relevance to the question
            - Availability of supporting facts""",
            contexts_list=reasoning_paths
        )

        # Step 4: Extract and refine the final answer
        raw_answer = await self.generate(
            instruction=f"""From the selected reasoning path: {selected_path}
            Extract the exact answer span from the relevant document.
            Ensure the answer is precise and matches the question format.""",
            context=selected_path
        )
        refined_answer = await self.revise(
            instruction="""Refine the extracted answer:
            - Ensure it matches the expected format
            - Verify factual correctness
            - Remove any ambiguity""",
            context=raw_answer
        )

        # Step 5: Collect and summarize supporting evidence
        supporting_facts = await self.summarize(
            instruction=f"""Summarize the supporting facts for the answer: {refined_answer}
            Include:
            - Key sentences from documents
            - Titles of relevant documents
            - Specific evidence chains""",
            context=selected_path
        )

        # Final Output
        return {
            "answer": refined_answer,
            "supporting_facts": supporting_facts
        }