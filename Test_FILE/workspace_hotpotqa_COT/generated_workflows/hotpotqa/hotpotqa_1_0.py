# Workflow ID: hotpotqa_1_0
# Benchmark: hotpotqa
# Data Indices: [0, 3]

class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio
        
        # Step 1: Determine question type and strategy
        strategy_instruction = """
        Analyze the given question carefully. Classify it into one of these types:
        - Bridge Question: Requires connecting two or more documents through a shared entity
        - Comparison Question: Asks to compare properties (e.g., value, date, size) between entities
        - Compositional Question: Combines multiple facts to derive an answer
        - Date/Time Question: Asks about when something happened
        
        Also, identify the target entity or concept the question is asking about.
        Provide your classification and target clearly in JSON format:
        {
          "question_type": "bridge|comparison|compositional|date",
          "target_entity": "the main subject being asked about"
        }
        """
        strategy_result = await self.generate(instruction=strategy_instruction, context=self.problem_text)
        
        # Step 2: Extract all relevant entities from the full problem text
        entity_extraction_instruction = f"""
        Based on the original problem and the identified question type ({strategy_result}),
        extract all named entities mentioned in the context documents that could be relevant to answering the question.
        Focus on people, places, organizations, products, species, events, dates, and concepts directly tied to the target entity.
        Return only the list of unique entities as a JSON array:
        ["entity1", "entity2", ...]
        """  
        entities = await self.generate(instruction=entity_extraction_instruction, context=self.problem_text)
        
        # Step 3: For each document, extract key facts relevant to the target entity
        doc_facts_instructions = [
            f"""
            Analyze Document {i+1} and extract all sentences that mention any of these entities: {entities}.
            For each sentence, summarize its key fact or claim in a concise way.
            Format as a JSON object mapping entity to list of facts:
            {{
              "entity1": ["fact1", "fact2"],
              ...
            }}
            """,
            f"""
            Analyze Document {i+2} and extract all sentences that mention any of these entities: {entities}.
            For each sentence, summarize its key fact or claim in a concise way.
            Format as a JSON object mapping entity to list of facts:
            {{
              "entity1": ["fact1", "fact2"],
              ...
            }}
            """
        ]  # This would normally loop over all docs — simplified here for brevity

        # In practice, you'd do this in parallel for efficiency:
        doc_facts_results = await asyncio.gather(*[
            self.generate(
                instruction=f"Analyze Document {idx+1} and extract all facts related to entities: {entities}.",
                context=doc_content
            )
            for idx, doc_content in enumerate(self.problem_text.split("Document ")) if idx > 0
        ])
        
        # Step 4: Build reasoning chain based on the question type
        reasoning_chain_instruction = f"""
        Using the extracted entities and facts from all documents, build a logical reasoning chain that leads to the answer.
        If it's a bridge question, identify the connecting entity between documents.
        If it's a comparison, compare the values/facts for the two entities involved.
        If it's compositional, combine multiple facts logically.
        If it's a date/time question, find the relevant event and its timing.

        Present your reasoning chain as a numbered list of steps:
        1. [Step 1 description]
        2. [Step 2 description]
        ...
        Finally, state the answer explicitly in a single sentence at the end.
        """
        reasoning_chain = await self.generate(
            instruction=reasoning_chain_instruction,
            context="\n".join(doc_facts_results)
        )
        
        # Step 5: Final synthesis and answer validation
        final_answer_instruction = f"""
        Based on the reasoning chain below, produce the final answer in a clear, concise manner.
        Ensure the answer matches the exact wording expected by the question.
        
        Reasoning Chain:
        {reasoning_chain}
        
        Now, output ONLY the final answer in plain text, without additional explanation.
        """
        final_answer = await self.generate(instruction=final_answer_instruction, context="")
        
        return final_answer