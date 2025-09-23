# Workflow ID: hotpotqa_226_0
# Benchmark: hotpotqa
# Data Indices: [234]

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

        # Step 1: Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Identify all named entities mentioned in the question.
            - Provide structured output with categories:
              * Question Type: [bridge/comparison/compositional]
              * Entities: [list of entities]""",
            context=""
        )

        # Parse initial analysis
        question_type = "bridge" if "bridge" in initial_analysis.lower() else "comparison" if "comparison" in initial_analysis.lower() else "compositional"
        entities = [line.split(":")[1].strip() for line in initial_analysis.split("\n") if "Entities" in line][0].split(", ")

        # Step 2: Parallel exploration of entities across documents
        exploration_tasks = [
            self.generate(
                instruction=f"""Find all mentions of '{entity}' across documents:
                - Identify relevant sentences or paragraphs.
                - Focus on facts that connect '{entity}' to the question.""",
                context=""
            ) for entity in entities
        ]
        entity_explorations = await asyncio.gather(*exploration_tasks)

        # Step 3: Construct reasoning chain (conditional branching)
        if question_type == "bridge":
            reasoning_chain = await self.ensemble(
                instruction="""Synthesize information to build a reasoning chain:
                - Identify shared entities across documents.
                - Connect entities logically to answer the question.""",
                contexts_list=entity_explorations
            )
        elif question_type == "comparison":
            reasoning_chain = await self.ensemble(
                instruction="""Compare properties across documents:
                - Extract comparable attributes.
                - Determine which entity satisfies the comparison criteria.""",
                contexts_list=entity_explorations
            )
        else:  # Compositional
            reasoning_chain = await self.ensemble(
                instruction="""Combine multiple facts to derive the answer:
                - Identify complementary information across documents.
                - Synthesize facts into a coherent reasoning chain.""",
                contexts_list=entity_explorations
            )

        # Step 4: Extract and validate answer (iterative loop)
        max_iterations = 3
        for iteration in range(max_iterations):
            answer = await self.generate(
                instruction=f"""Extract the precise answer span from the reasoning chain:
                - Reasoning Chain: {reasoning_chain}
                - Ensure the answer is a short text span or yes/no response.""",
                context=""
            )

            validation = await self.revise(
                instruction=f"""Validate the answer against the reasoning chain:
                - Answer: {answer}
                - Reasoning Chain: {reasoning_chain}
                - Identify inconsistencies or missing details.""",
                context=reasoning_chain
            )

            if "error" not in validation.lower() and "inconsistent" not in validation.lower():
                break  # Exit loop if validation passes
            else:
                reasoning_chain = validation  # Refine reasoning chain based on feedback

        return answer