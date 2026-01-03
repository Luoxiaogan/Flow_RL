# Workflow ID: hotpotqa_99_0
# Benchmark: hotpotqa
# Data Indices: [148, 52]

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
        
        # Initial Parallel Analysis
        initial_tasks = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities, numbers, and relationships:
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ),
            self.generate(
                instruction="""Classify this question:
                1. Is it a bridge question? (connecting entities across documents)
                2. Is it a comparison question? (comparing properties)
                3. Is it a compositional question? (combining multiple facts)
                Provide structured classification.""",
                context=""
            ),
            self.generate(
                instruction="""Assess which documents are likely to contain relevant information:
                - Identify key terms in the question
                - Match these terms to document titles and content
                - Rank documents by relevance""",
                context=""
            )
        )
        entities, question_type, document_relevance = initial_tasks

        # Refine Entities and Classifications
        refined_entities = await self.revise(
            instruction="Remove duplicates and irrelevant entries from the entity list.",
            context=entities
        )
        refined_question_type = await self.revise(
            instruction="Clarify and confirm the question classification.",
            context=question_type
        )

        # Conditional Branching Based on Question Type
        if "bridge" in refined_question_type.lower():
            # Bridge Question Workflow
            bridge_tasks = await asyncio.gather(
                self.generate(
                    instruction=f"""Find shared entities between documents:
                    Entities: {refined_entities}
                    Relevant Documents: {document_relevance}
                    Identify common entities that connect different documents.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Build reasoning chain using shared entities:
                    Entities: {refined_entities}
                    Relevant Documents: {document_relevance}
                    Construct logical connections between entities to answer the question.""",
                    context=""
                )
            )
            shared_entities, reasoning_chain = bridge_tasks
            
            final_answer = await self.ensemble(
                instruction="Select the most coherent and factually supported reasoning chain.",
                contexts_list=[shared_entities, reasoning_chain]
            )
            
        elif "comparison" in refined_question_type.lower():
            # Comparison Question Workflow
            comparison_tasks = await asyncio.gather(
                self.generate(
                    instruction=f"""Extract relevant properties for comparison:
                    Entities: {refined_entities}
                    Relevant Documents: {document_relevance}
                    Identify properties mentioned in the question and extract their values.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Perform comparison between extracted properties:
                    Properties: [extracted_properties]
                    Compare values to determine which meets the question's criteria.""",
                    context=""
                )
            )
            properties, comparison_result = comparison_tasks
            
            final_answer = await self.ensemble(
                instruction="Select the result of the comparison that directly answers the question.",
                contexts_list=[properties, comparison_result]
            )
            
        else:
            # Compositional Question Workflow
            compositional_tasks = await asyncio.gather(
                self.generate(
                    instruction=f"""Identify key facts needed to compose the answer:
                    Entities: {refined_entities}
                    Relevant Documents: {document_relevance}
                    List facts required to build the complete answer.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Combine identified facts into a coherent answer:
                    Facts: [identified_facts]
                    Synthesize these facts into a single, precise answer.""",
                    context=""
                )
            )
            key_facts, composed_answer = compositional_tasks
            
            final_answer = await self.ensemble(
                instruction="Select the most complete and accurate composed answer.",
                contexts_list=[key_facts, composed_answer]
            )
        
        # Final Answer Refinement
        refined_final_answer = await self.revise(
            instruction="Ensure the final answer is concise, precise, and directly addresses the question.",
            context=final_answer
        )
        
        return refined_final_answer