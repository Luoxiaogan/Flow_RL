# Workflow ID: hotpotqa_106_0
# Benchmark: hotpotqa
# Data Indices: [240, 38]

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
        import re

        # Step 1: Classify question type and extract key entities
        classification = await self.generate(
            instruction="""Classify the question type:
            - Is it a bridge question (connecting entities)?
            - Is it a comparison question (comparing attributes)?
            - Is it a compositional question (combining facts)?
            
            Extract key entities and relationships mentioned in the question.
            Format the output as:
            Question Type: [type]
            Key Entities: [entity1, entity2, ...]""",
            context=""
        )

        # Parse classification result
        question_type = re.search(r"Question Type:\s*(.+)", classification).group(1).strip()
        key_entities = re.findall(r"Key Entities:\s*\[(.+)\]", classification)[0].split(", ")

        # Step 2: Parallel document processing to extract relevant facts
        document_prompts = [
            f"""Extract facts related to the following entities from this document:
            Entities: {', '.join(key_entities)}
            Format the output as:
            Entity: [entity]
            Fact: [fact]
            Source: [document title]"""
            for _ in range(len(re.findall("Document \d+", self.problem_text)))
        ]
        document_facts = await asyncio.gather(
            *[self.generate(instruction=prompt, context="") for prompt in document_prompts]
        )

        # Combine facts into a single context
        combined_facts = "\n".join(document_facts)

        # Step 3: Build reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted facts:
            {combined_facts}
            
            Build a reasoning chain to answer the question:
            - Start with the key entities.
            - Connect them through intermediate entities/facts.
            - Ensure each link is supported by evidence.
            Format the chain as:
            [Entity1] -> [Intermediate Entity] -> [Entity2] -> [Answer]""",
            context=classification
        )

        # Step 4: Refine reasoning chain iteratively
        refined_chain = reasoning_chain
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                {refined_chain}
                
                Check for logical consistency and factual accuracy.
                Identify any gaps or unsupported links.""",
                context=combined_facts
            )
            if "error" in validation.lower() or "gap" in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"""Fix issues in the reasoning chain:
                    Issues: {validation}
                    
                    Revise the chain to address these problems.""",
                    context=refined_chain
                )
            else:
                break

        # Step 5: Synthesize answer
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the final answer from the reasoning chain:
                {refined_chain}
                
                Ensure the answer is precise and matches the question format.""",
                context=combined_facts
            ),
            self.generate(
                instruction=f"""Provide an alternative interpretation of the reasoning chain:
                {refined_chain}
                
                Consider other possible answers based on the facts.""",
                context=combined_facts
            )
        )
        final_answer = await self.ensemble(
            instruction="""Select the most accurate and well-supported answer.
            Prioritize answers with clear evidence from the documents.""",
            contexts_list=candidate_answers
        )

        return final_answer