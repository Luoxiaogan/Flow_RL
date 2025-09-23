# Workflow ID: hotpotqa_55_0
# Benchmark: hotpotqa
# Data Indices: [456, 245]

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

        # Step 1: Initial Analysis - Classify Question Type and Extract Entities
        initial_analysis = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting entities across documents
            - Comparison: Requires comparing properties across documents
            - Compositional: Requires combining multiple facts
            
            Then, extract all named entities, numbers, and relationships from the documents.
            Format the output as:
            Question Type: [type]
            Entities: [list of entities and relationships]""",
            context=""
        )

        # Step 2: Parallel Processing - Extract Relevant Information
        question_type = "Bridge" if "Bridge" in initial_analysis else "Comparison" if "Comparison" in initial_analysis else "Compositional"
        entities = initial_analysis.split("Entities:")[-1].strip()

        parallel_tasks = []
        if question_type == "Bridge":
            parallel_tasks.append(
                self.generate(
                    instruction=f"""Extract shared entities and their relationships from the documents.
                    Focus on entities that connect multiple documents.
                    Entities to consider: {entities}""",
                    context=""
                )
            )
        elif question_type == "Comparison":
            parallel_tasks.append(
                self.generate(
                    instruction=f"""Extract properties to compare from the documents.
                    Focus on numerical values, dates, or other comparable attributes.
                    Entities to consider: {entities}""",
                    context=""
                )
            )
        else:  # Compositional
            parallel_tasks.append(
                self.generate(
                    instruction=f"""Extract multiple facts that need to be combined to answer the question.
                    Focus on logical connections between entities.
                    Entities to consider: {entities}""",
                    context=""
                )
            )

        extracted_info_list = await asyncio.gather(*parallel_tasks)

        # Step 3: Refine Extracted Information
        refined_info_list = await asyncio.gather(
            *[self.revise(
                instruction="Refine the extracted information for clarity and accuracy.",
                context=info
            ) for info in extracted_info_list]
        )

        # Step 4: Construct Reasoning Chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain that connects the refined information.
            Ensure the chain is factually correct and supported by evidence from the documents.
            Refined Information: {refined_info_list}""",
            context=""
        )

        # Step 5: Answer Synthesis
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the exact answer span from the documents based on the reasoning chain.
                Ensure the answer is concise and directly answers the question.
                Reasoning Chain: {reasoning_chain}""",
                context=""
            ),
            self.generate(
                instruction=f"""Provide an alternative interpretation of the reasoning chain.
                Extract a different answer span if possible.
                Reasoning Chain: {reasoning_chain}""",
                context=""
            )
        )

        final_answer = await self.ensemble(
            instruction="Select the most accurate and concise answer based on the reasoning chain.",
            contexts_list=candidate_answers
        )

        return final_answer