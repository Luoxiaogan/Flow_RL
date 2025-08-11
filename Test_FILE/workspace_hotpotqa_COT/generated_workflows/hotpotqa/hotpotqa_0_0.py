# Workflow ID: hotpotqa_0_0
# Benchmark: hotpotqa
# Data Indices: [1, 2]

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
        
        # Step 1: Identify the question type and core query
        instruction_1 = """
        Analyze the question carefully. Determine what type of reasoning is required:
        - Bridge Question: Requires connecting two pieces of information through a shared entity
        - Comparison Question: Requires comparing properties of two entities
        - Compositional Question: Requires combining multiple facts to derive an answer
        
        Also, identify the primary entity or concept being queried (e.g., person, place, event).
        Return your result in JSON format with keys: 'question_type', 'primary_entity'.
        Example: {"question_type": "bridge", "primary_entity": "William Prescott"}
        """
        analysis_result = await self.generate(instruction=instruction_1, context=self.problem_text)
        
        # Step 2: Extract the key entity mentioned in the question
        instruction_2 = f"""
        Based on the analysis above, extract the exact phrase(s) that refer to the main subject of the question.
        For example, if the question is about the birthplace of someone, extract their name.
        If it's a comparison, extract both entities being compared.
        Return only the raw text of the entity or entities involved in the question.
        Do NOT add explanations or formatting — just the string(s).
        """
        entity_result = await self.generate(instruction=instruction_2, context=analysis_result)
        
        # Step 3: Find documents containing this entity
        instruction_3 = f"""
        Search all provided context documents for mentions of the following entity: "{entity_result}".
        List each document number (1-based index) where the entity appears.
        Include brief context from each matching document (first sentence or two).
        Format as a list of dictionaries: [{{"doc_id": int, "context": str}}]
        """
        doc_matches = await self.generate(instruction=instruction_3, context=self.problem_text)
        
        # Step 4: For bridge questions, find the next hop (the connecting entity)
        instruction_4 = f"""
        You are solving a {analysis_result['question_type']} question involving the entity "{entity_result}".
        From the matched documents, identify which other document(s) contain additional relevant facts that help answer the original question.
        Specifically, look for:
        - Documents that mention the same entity but in a different context (e.g., birthplace, profession, affiliations)
        - Documents that introduce a new entity that connects to the original one (e.g., "born in X" → "X has prep schools")
        
        Output a list of potential bridge documents with short descriptions of how they relate to the original entity.
        Format as: [{{"doc_id": int, "reason": str}}]
        """
        bridge_candidates = await self.generate(instruction=instruction_4, context=doc_matches)
        
        # Step 5: Build full reasoning chain (for bridge questions)
        instruction_5 = f"""
        Construct a step-by-step reasoning chain that leads from the original question to the final answer.
        Start with the entity "{entity_result}".
        Then describe how you move from Document A to Document B via a bridge entity or fact.
        Finally, state the answer derived from the chain.
        
        Your output must be structured like this:
        Chain: 
        1. Entity: {entity_result}
        2. From Document X: [fact about entity]
        3. This connects to Document Y via [bridge entity/fact]
        4. From Document Y: [supporting fact for answer]
        5. Therefore, the answer is: [final answer]
        """
        reasoning_chain = await self.generate(instruction=instruction_5, context=bridge_candidates)
        
        # Step 6: Validate and refine the chain
        instruction_6 = f"""
        Review the reasoning chain below. Critique it for logical gaps, missing steps, or ambiguous references.
        If any part lacks clarity or support, revise it accordingly.
        Ensure every claim is grounded in the provided documents.
        
        Original Chain:
        {reasoning_chain}
        
        Provide the revised chain in the same structure as before.
        """
        refined_chain = await self.revise(instruction=instruction_6, context=reasoning_chain)
        
        # Step 7: Extract precise answer span from the final document
        instruction_7 = f"""
        From the final document in the reasoning chain, locate the specific sentence(s) that directly support the conclusion.
        Extract only the exact answer span (a short phrase or word) that answers the original question.
        Do not paraphrase — return the original wording found in the text.
        """
        answer_span = await self.generate(instruction=instruction_7, context=refined_chain)
        
        # Step 8: Final ensemble check – if multiple candidates exist, choose best
        instruction_8 = f"""
        You have produced one candidate answer: "{answer_span}".
        However, due to ambiguity in some cases, generate up to three alternative interpretations or answer spans based on the same reasoning chain.
        Then, evaluate them against the original question and supporting facts to select the most accurate and well-supported one.
        
        Output format:
        - Candidate 1: [text]
        - Candidate 2: [text]
        - Candidate 3: [text]
        - Best Answer: [chosen answer]
        """  
        final_answer = await self.ensemble(instruction=instruction_8, contexts=[answer_span])
        
        return final_answer