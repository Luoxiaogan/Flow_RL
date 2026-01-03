# Workflow ID: hotpotqa_35_0
# Benchmark: hotpotqa
# Data Indices: [467]

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
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - Identify the main subject(s) of the question
            - Determine the type of reasoning required
            - List all named entities mentioned in the question""",
            context=""
        )

        # Step 2: Entity Linking - Find mentions of key entities across documents
        entities = await self.generate(
            instruction=f"""Extract mentions of the following entities across all documents:
            {initial_analysis}
            
            For each entity:
            - List the documents where it appears
            - Identify its role or significance in each document
            - Note any relationships or connections to other entities""",
            context=initial_analysis
        )

        # Step 3: Parallel Hypothesis Generation - Construct potential reasoning chains
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Construct a reasoning chain for a bridge question:
                {entities}
                
                Connect entities through shared relationships or concepts""",
                context=entities
            ),
            self.generate(
                instruction=f"""Construct a reasoning chain for a comparison question:
                {entities}
                
                Compare properties or attributes of the entities""",
                context=entities
            ),
            self.generate(
                instruction=f"""Construct a reasoning chain for a compositional question:
                {entities}
                
                Combine multiple facts to derive the answer""",
                context=entities
            )
        )

        # Step 4: Ensemble Selection - Choose the most credible reasoning chain
        selected_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains and select the most credible one:
            - Check for logical consistency
            - Verify factual accuracy
            - Ensure alignment with the question type""",
            contexts_list=reasoning_chains
        )

        # Step 5: Answer Extraction - Extract the precise answer span
        answer_extraction = await self.generate(
            instruction=f"""Extract the exact answer span from the selected reasoning chain:
            {selected_chain}
            
            Ensure the answer is a short, factual phrase directly from the text""",
            context=selected_chain
        )

        # Step 6: Validation and Refinement - Validate the answer and refine if necessary
        final_answer = await self.revise(
            instruction="""Validate the extracted answer:
            - Ensure it matches the reasoning chain
            - Confirm it is factually correct
            - Refine if necessary to improve clarity or precision""",
            context=answer_extraction
        )

        return final_answer