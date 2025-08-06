class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem # Assumes problem is a pre-processed string
        self.llm = create(config)

        # All available operators are initialized here for your use.
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        This is where you implement the core problem-solving logic.
        You can use any of the operators initialized above.
        """
        import asyncio
        
        # Step 1: Parallel extraction and deep question analysis
        extraction_task = self.generate(
            instruction="Extract ALL numbers, dates, entities, facts, and relationships from the passage. List every occurrence separately, even if values repeat. Include context for each number."
        )
        
        question_interpretation_task = self.generate(
            instruction="Analyze the question carefully: 1) Is it asking for a sum/total or a single value? 2) Look for keywords like 'total', 'combined', 'each', 'per', 'altogether'. 3) Could the question be ambiguous? List multiple possible interpretations if unclear."
        )
        
        # Execute in parallel
        information_extraction, question_interpretation = await asyncio.gather(
            extraction_task,
            question_interpretation_task
        )
        
        # Step 2: Create comprehensive context
        combined_context = f"EXTRACTED DATA:\n{information_extraction}\n\nQUESTION ANALYSIS:\n{question_interpretation}"
        
        # Step 3: Generate multiple interpretations in parallel
        # Each strategy considers different possible meanings
        
        # Strategy 1: Conservative interpretation (single value)
        solution_conservative = self.generate(
            instruction="Answer assuming the question asks for a SINGLE value, not a sum. If multiple instances exist with the same value, return that common value. If different values exist, return the first or most relevant one.",
            context=combined_context
        )
        
        # Strategy 2: Summation interpretation
        solution_sum = self.generate(
            instruction="Answer by summing ALL relevant values found in the passage. Add up every instance that matches what the question asks for.",
            context=combined_context
        )
        
        # Strategy 3: Counting interpretation
        solution_count = self.generate(
            instruction="Answer by counting the NUMBER of occurrences or instances, not their values. Count how many times something happens.",
            context=combined_context
        )
        
        # Strategy 4: Contextual interpretation
        solution_contextual = self.generate(
            instruction="Consider the grammatical structure and context of the question. Does it refer to a specific event or all events? Is there implicit context suggesting which answer makes most sense?",
            context=combined_context
        )
        
        # Strategy 5: Literal interpretation
        solution_literal = self.generate(
            instruction="Take the question at face value without overthinking. What's the most straightforward answer based on direct text matching?",
            context=combined_context
        )
        
        # Execute all interpretations in parallel
        candidates = await asyncio.gather(
            solution_conservative,
            solution_sum,
            solution_count,
            solution_contextual,
            solution_literal
        )
        
        # Step 4: Smart ensemble considering question ambiguity
        preliminary_answer = await self.ensemble(
            instruction="Review all interpretations. If the question is unambiguous, select the consensus answer. If ambiguous, prefer the simplest interpretation (single value over sum, specific over general). Extract just the numeric answer or text span.",
            contexts_to_ensemble=candidates
        )
        
        # Step 5: Validation against common patterns
        validated_answer = await self.revise(
            instruction="Check if this answer makes logical sense: Is it within reasonable bounds? For 'how many yards' questions, is the answer a plausible yardage? If the answer seems like a sum but all components are identical, consider returning the single value instead.",
            context_to_revise=preliminary_answer
        )
        
        # Step 6: Final formatting
        final_answer = await self.generate(
            instruction="Return ONLY the answer with no explanation: just the number, date, or exact text span from the passage.",
            context=validated_answer
        )
        
        return final_answer