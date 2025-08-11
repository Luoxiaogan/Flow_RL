# Workflow ID: hotpotqa_0_0
# Benchmark: hotpotqa
# Data Indices: [1, 0]

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
        
        # Step 1: Identify the core question type and target entity
        instruction_1 = """
        Analyze the question carefully and determine:
        - What is the main entity or concept being asked about?
        - Is this a bridge question, comparison question, or compositional question?
        - If it's a bridge question, identify the likely bridge entity that connects two or more documents.
        - If it's a comparison question, identify the two entities being compared.
        - If it's a compositional question, break down the required facts into sub-questions.

        Output your analysis as a JSON object with keys:
        - 'question_type': string ("bridge", "comparison", or "compositional")
        - 'target_entity': string (the primary subject of the question)
        - 'bridge_entity': string (if applicable, else null)
        - 'comparison_entities': list of strings (if applicable, else empty list)
        - 'sub_questions': list of strings (if applicable, else empty list)
        """
        analysis_json_str = await self.generate(instruction=instruction_1, context=self.problem_text)
        
        # Parse the JSON output from the first step
        try:
            import json
            analysis = json.loads(analysis_json_str)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse analysis JSON from generate step.")
        
        # Step 2: Based on the identified type, extract relevant documents and bridge info
        if analysis['question_type'] == 'bridge':
            instruction_2 = f"""
            You have determined this is a bridge question targeting '{analysis['target_entity']}' 
            connected via the bridge entity '{analysis['bridge_entity']}'. 

            Now, scan all context documents to find:
            - Which documents mention the bridge entity?
            - From those documents, extract sentences that contain information about the target entity.
            - Also extract any supporting facts that help link the bridge entity to the target entity.

            Format your response as a JSON array of objects with keys:
            - 'document_id': int (the index of the document in the original list)
            - 'relevant_sentences': list of strings (sentences containing relevant info)
            - 'supporting_facts': list of strings (facts that support the connection between bridge and target)
            """
            bridge_info_json_str = await self.generate(instruction=instruction_2, context=self.problem_text)
            try:
                bridge_info = json.loads(bridge_info_json_str)
            except json.JSONDecodeError:
                raise ValueError("Failed to parse bridge info JSON from generate step.")

            # Step 3: Synthesize the answer using the extracted facts
            facts_str = "\n".join([
                f"Doc {doc['document_id']}: {fact}"
                for doc in bridge_info
                for fact in doc['supporting_facts']
            ])
            
            instruction_3 = f"""
            Using the following supporting facts, derive the final answer:

            {facts_str}

            The question was: "{self.problem_text}"

            Provide a concise, precise answer that directly addresses the question.
            Include the exact span(s) of text from the documents that support your answer.
            Format as:
            - Answer: [your answer]
            - Supporting Facts: [list of sentence spans that justify the answer]
            """
            final_answer = await self.generate(instruction=instruction_3, context="")
            
        elif analysis['question_type'] == 'comparison':
            instruction_2 = f"""
            This is a comparison question comparing entities: {', '.join(analysis['comparison_entities'])}.
            Identify the property being compared (e.g., founding date, nationality, etc.).

            For each entity, locate the relevant document(s) that provide the comparative value.
            Extract the specific values from those documents.

            Output as a JSON object:
            - 'property': string (the attribute being compared)
            - 'values': dict mapping entity name to its value
            """  
            comparison_data_json_str = await self.generate(instruction=instruction_2, context=self.problem_text)
            try:
                comparison_data = json.loads(comparison_data_json_str)
            except json.JSONDecodeError:
                raise ValueError("Failed to parse comparison data JSON from generate step.")
            
            instruction_3 = f"""
            Given these values:
            {json.dumps(comparison_data, indent=2)}

            Determine which entity has the higher/lower value (depending on the property).
            Provide a clear answer stating which entity wins the comparison.
            Include the exact sentence from the source documents that supports the value used.
            """
            final_answer = await self.generate(instruction=instruction_3, context="")

        elif analysis['question_type'] == 'compositional':
            instruction_2 = f"""
            This is a compositional question requiring multiple facts. Break it down into sub-questions:
            {', '.join(analysis['sub_questions'])}

            For each sub-question, find the document(s) that contain the answer.
            Extract the relevant sentence(s) for each sub-question.

            Output as a JSON array of objects:
            - 'sub_question': string
            - 'answer': string
            - 'source_sentence': string (the sentence from the document that contains the answer)
            """
            sub_q_results_json_str = await self.generate(instruction=instruction_2, context=self.problem_text)
            try:
                sub_q_results = json.loads(sub_q_results_json_str)
            except json.JSONDecodeError:
                raise ValueError("Failed to parse sub-question results JSON from generate step.")
            
            instruction_3 = f"""
            Combine the following answers to form a complete response to the original question:
            {json.dumps(sub_q_results, indent=2)}

            Original question: "{self.problem_text}"

            Provide a concise answer that integrates all pieces of information.
            Cite the source sentences for each piece of information used.
            """
            final_answer = await self.generate(instruction=instruction_3, context="")

        else:
            raise ValueError(f"Unknown question type: {analysis['question_type']}")

        return final_answer