# Workflow ID: hotpotqa_282_0
# Benchmark: hotpotqa
# Data Indices: [377, 310]

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

        # Step 1: Initial Analysis - Classify Question and Extract Entities
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Requires connecting shared entities across documents.
            2. Comparison Question: Involves comparing properties or attributes.
            3. Compositional Question: Combines multiple facts to derive the answer.
            Also, extract all named entities, numbers, and relationships from the context documents.
            Format the output as:
            Question Type: [type]
            Entities: [list of entities]""",
            context=""
        )

        # Parse classification and entities
        question_type = "Bridge" if "Bridge" in classification else "Comparison" if "Comparison" in classification else "Compositional"
        entities = classification.split("Entities:")[1].strip()

        # Step 2: Parallel Exploration - Build Reasoning Chains
        reasoning_tasks = [
            self.generate(
                instruction=f"""For the entity '{entity}', hypothesize its role in answering the question.
                Consider connections to other entities and relevant facts from the context documents.""",
                context=classification
            )
            for entity in entities.split(", ")
        ]
        reasoning_chains = await asyncio.gather(*reasoning_tasks)

        # Step 3: Conditional Branching - Strategy Selection
        if question_type == "Bridge":
            reasoning_chain = await self.generate(
                instruction=f"""Connect the shared entities across documents to form a reasoning chain.
                Entities: {entities}
                Hypotheses: {reasoning_chains}""",
                context=classification
            )
        elif question_type == "Comparison":
            reasoning_chain = await self.generate(
                instruction=f"""Compare the properties or attributes of the entities to derive the answer.
                Entities: {entities}
                Hypotheses: {reasoning_chains}""",
                context=classification
            )
        else:  # Compositional
            reasoning_chain = await self.generate(
                instruction=f"""Combine multiple facts from the hypotheses to derive the answer.
                Entities: {entities}
                Hypotheses: {reasoning_chains}""",
                context=classification
            )

        # Step 4: Iterative Refinement - Validate and Adjust
        refined_chain = reasoning_chain
        for _ in range(3):  # Limit iterations
            validation = await self.revise(
                instruction="Validate the reasoning chain and correct any errors.",
                context=refined_chain
            )
            if "error" not in validation.lower():
                break
            refined_chain = validation

        # Step 5: Final Synthesis - Extract Answer and Assemble Evidence
        answer = await self.summarize(
            instruction="Extract the precise answer span from the refined reasoning chain.",
            context=refined_chain
        )
        evidence = await self.summarize(
            instruction="Assemble supporting facts into a structured format.",
            context=refined_chain
        )

        return {
            "answer": answer.strip(),
            "supporting_facts": evidence.strip()
        }