# Workflow ID: hotpotqa_198_0
# Benchmark: hotpotqa
# Data Indices: [102, 57]

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

        # Step 1: Analyze the question type and extract key components
        question_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Identify the question type: bridge, comparison, or compositional.
            2. Extract key entities, relationships, and constraints.
            3. Formulate a preliminary reasoning strategy.
            Provide structured output.""",
            context=""
        )

        # Step 2: Dynamically branch based on question type
        if "bridge" in question_analysis.lower():
            # Bridge question: Identify shared entities
            bridge_entities = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Extract entities from Document {i+1} that could serve as bridge entities.
                    Focus on named entities, relationships, and key phrases.""",
                    context=""
                ) for i in range(10)]  # Assuming up to 10 documents
            )
            best_entity = await self.ensemble(
                instruction="Select the most plausible bridge entity based on contextual relevance.",
                contexts_list=bridge_entities
            )
            reasoning_chain = await self.generate(
                instruction=f"""Using the bridge entity '{best_entity}', construct a reasoning chain:
                - Locate related information in other documents.
                - Connect the dots to answer the question.""",
                context=question_analysis
            )
        elif "comparison" in question_analysis.lower():
            # Comparison question: Extract comparable properties
            properties = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Extract relevant properties (e.g., dates, numbers) from Document {i+1}.
                    Focus on information that can be compared.""",
                    context=""
                ) for i in range(10)]
            )
            comparison_result = await self.generate(
                instruction=f"""Compare the extracted properties:
                - Determine which entity satisfies the comparison criteria.
                - Provide a clear justification.""",
                context="\n".join(properties)
            )
            reasoning_chain = comparison_result
        else:
            # Compositional question: Combine multiple facts
            facts = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Extract key facts from Document {i+1}.
                    Focus on information that contributes to answering the question.""",
                    context=""
                ) for i in range(10)]
            )
            synthesized_facts = await self.ensemble(
                instruction="Synthesize the extracted facts into a coherent reasoning chain.",
                contexts_list=facts
            )
            reasoning_chain = synthesized_facts

        # Step 3: Refine and validate the reasoning chain
        refined_chain = await self.revise(
            instruction="""Critique and refine the reasoning chain:
            - Ensure logical consistency.
            - Verify factual accuracy against the documents.
            - Address any gaps or ambiguities.""",
            context=reasoning_chain
        )

        # Step 4: Extract and summarize the final answer
        final_answer = await self.generate(
            instruction="""Extract the final answer from the refined reasoning chain:
            - Ensure it matches the required format (short text span or yes/no).
            - Provide supporting facts from the documents.""",
            context=refined_chain
        )

        # Step 5: Summarize the entire process for clarity
        summary = await self.summarize(
            instruction="Summarize the reasoning process and final answer concisely.",
            context=final_answer
        )

        return summary