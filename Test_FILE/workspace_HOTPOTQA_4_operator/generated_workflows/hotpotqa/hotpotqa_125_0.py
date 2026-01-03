# Workflow ID: hotpotqa_125_0
# Benchmark: hotpotqa
# Data Indices: [460]

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

        # Phase 1: Question Analysis
        question_analysis = await self.generate(
            instruction="""Classify the question type and extract key entities/relationships:
            - Is it a bridge, comparison, or compositional question?
            - Identify named entities, relationships, or properties mentioned in the question.
            - Provide structured output with clear categories.""",
            context=""
        )

        # Phase 2: Parallel Document Exploration
        entities = await self.generate(
            instruction=f"""Extract all relevant entities/relationships from the question analysis:
            {question_analysis}
            
            Focus on:
            - Named entities (e.g., people, places, organizations)
            - Relationships or properties mentioned
            - Any specific constraints or conditions.""",
            context=question_analysis
        )

        # Split entities into individual items
        entity_list = [e.strip() for e in entities.split('\n') if e.strip()]

        # Explore documents in parallel
        document_explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Find information related to '{entity}' in the provided documents:
                - Focus on factual statements about '{entity}'
                - Include any relationships or properties associated with '{entity}'
                - Summarize key facts in bullet points.""",
                context=""
            ) for entity in entity_list]
        )

        # Summarize extracted information
        summarized_facts = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Condense the following information into key facts:
                {doc_exp}""",
                context=doc_exp
            ) for doc_exp in document_explorations]
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain using the summarized facts:
            Facts:
            {summarized_facts}
            
            Instructions:
            - Connect the facts logically to answer the question
            - Ensure each step in the chain is supported by at least one fact
            - Highlight any assumptions or missing links.""",
            context="\n".join(summarized_facts)
        )

        refined_chain = await self.revise(
            instruction=f"""Refine the reasoning chain for clarity and correctness:
            Original Chain:
            {reasoning_chain}
            
            Instructions:
            - Resolve any ambiguities or gaps
            - Ensure logical consistency
            - Add supporting evidence from the documents.""",
            context=reasoning_chain
        )

        # Phase 4: Answer Extraction and Validation
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the precise answer from the reasoning chain:
                Chain:
                {refined_chain}
                
                Instructions:
                - Focus on short text spans or yes/no responses
                - Ensure the answer is directly supported by the chain""",
                context=refined_chain
            ),
            self.generate(
                instruction=f"""Provide an alternative interpretation of the reasoning chain:
                Chain:
                {refined_chain}
                
                Instructions:
                - Consider other possible answers
                - Ensure the alternative is still supported by the chain""",
                context=refined_chain
            )
        )

        final_answer = await self.ensemble(
            instruction=f"""Select the best answer based on factual correctness and alignment with supporting facts:
            Candidate Answers:
            {candidate_answers}
            
            Instructions:
            - Prioritize answers directly supported by the reasoning chain
            - Resolve any conflicts by analyzing context and relevance""",
            contexts_list=candidate_answers
        )

        return final_answer