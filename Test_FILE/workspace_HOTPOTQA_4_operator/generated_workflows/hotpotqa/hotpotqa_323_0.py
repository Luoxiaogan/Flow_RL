# Workflow ID: hotpotqa_323_0
# Benchmark: hotpotqa
# Data Indices: [113, 140]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        question_analysis, entity_extraction = await asyncio.gather(
            self.generate(
                instruction="""Classify the question type:
                1. Bridge Question: Connects documents through shared entities.
                2. Comparison Question: Compares properties across documents.
                3. Compositional Question: Combines multiple facts to derive an answer.
                Provide structured classification.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all named entities, relationships, and constraints:
                - Entities: Names, places, organizations, etc.
                - Relationships: Connections between entities.
                - Constraints: Conditions or limitations stated in the problem.""",
                context=""
            )
        )

        # Step 2: Build Reasoning Chain Based on Question Type
        if "bridge" in question_analysis.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Identify the 'bridge entity' and trace its connections across documents:
                Entities: {entity_extraction}
                Build a logical chain linking the documents through the bridge entity.""",
                context=entity_extraction
            )
        elif "comparison" in question_analysis.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Extract comparable attributes and determine their relationship:
                Entities: {entity_extraction}
                Compare properties using logical operators (e.g., earlier than, larger than).""",
                context=entity_extraction
            )
        else:  # Compositional question
            reasoning_chain = await self.generate(
                instruction=f"""Sequentially link facts across documents:
                Entities: {entity_extraction}
                Ensure each step logically follows from the previous one.""",
                context=entity_extraction
            )

        # Step 3: Validate and Refine Reasoning Chain
        validation = await self.revise(
            instruction=f"""Validate the reasoning chain:
            - Is it factually accurate?
            - Are there any gaps or ambiguities?
            Suggest improvements if necessary.""",
            context=reasoning_chain
        )
        refined_chain = await self.revise(
            instruction=f"""Refine the reasoning chain based on validation feedback:
            Validation: {validation}
            Address identified issues and ensure logical coherence.""",
            context=reasoning_chain
        )

        # Step 4: Extract Answer and Supporting Facts
        answer_extraction, supporting_facts = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the precise answer span from the final document:
                Reasoning Chain: {refined_chain}
                Ensure the answer is concise and directly supported by the text.""",
                context=refined_chain
            ),
            self.generate(
                instruction=f"""Identify supporting facts from different documents:
                Reasoning Chain: {refined_chain}
                Provide a transparent view of the evidence chain.""",
                context=refined_chain
            )
        )

        # Step 5: Final Output
        return {
            "answer": answer_extraction.strip(),
            "supporting_facts": supporting_facts.strip()
        }