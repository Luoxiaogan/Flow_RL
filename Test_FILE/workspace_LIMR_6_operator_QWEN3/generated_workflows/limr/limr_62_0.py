# Workflow ID: limr_62_0
# Benchmark: limr
# Data Indices: [317, 69]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # STEP 1: META-CLASSIFICATION - Understand the problem's epistemic structure
        classification = await self.generate(
            instruction="""Perform a deep meta-classification of this problem. Answer these questions:
            1. What primary mathematical domain does this belong to? (e.g., number theory, combinatorics, geometry)
            2. What secondary domains might be relevant?
            3. What type of reasoning is required? (constructive, existential, optimization, counting, etc.)
            4. What is the expected answer format? (integer, fraction, proof, etc.)
            5. Are there any obvious invariants, symmetries, or conserved quantities?
            6. What are the most promising solution strategies? Rank them by likelihood of success.
            7. What are the potential pitfalls or places where mistakes commonly occur?
            8. Estimate the number of non-trivial steps required.
            
            Format your response as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION STREAMS - Spawn multiple approaches based on classification
        # Extract top 3 strategies from classification (simplified parsing - in practice, use more robust extraction)
        strategy_extraction = await self.generate(
            instruction="""From the classification below, extract exactly three distinct solution strategies. 
            For each, provide a 50-word instruction that would guide a mathematician to pursue that approach.
            Format as: STRATEGY 1: <instruction>
                     STRATEGY 2: <instruction>
                     STRATEGY 3: <instruction>""",
            context=classification
        )

        # Split strategies (basic parsing - assumes consistent formatting)
        strategies = []
        for line in strategy_extraction.split('\n'):
            if line.startswith('STRATEGY') and ':' in line:
                strategies.append(line.split(':', 1)[1].strip())

        # If we didn't get 3 strategies, create fallbacks
        while len(strategies) < 3:
            strategies.append("Apply general mathematical problem-solving principles: break into cases, look for patterns, use symmetry, and verify with small examples.")

        # Generate parallel solution attempts
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Implement this solution strategy: {strategy}
                
                Requirements:
                - Show all key steps and reasoning
                - Be explicit about assumptions
                - Include any intermediate calculations
                - If you reach a dead end, explain why and what you learned
                - Format your final answer clearly at the end""",
                context=""
            ) for strategy in strategies[:3]]
        )

        # STEP 3: ADVERSARIAL VALIDATION - Critique each solution attempt
        critiques = await asyncio.gather(
            *[self.revise(
                instruction="""You are a skeptical mathematician reviewing this solution attempt. Your task:
                1. Find the weakest link in the reasoning
                2. Identify any unjustified assumptions
                3. Check for arithmetic or logical errors
                4. Verify that the answer satisfies all problem constraints
                5. Suggest specific improvements or corrections
                6. Assign a confidence score (0-100) based on rigor and completeness
                
                Be brutally honest. Your goal is to prevent false confidence.""",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # STEP 4: CONFIDENCE-BASED FILTERING - Keep only high-confidence solutions
        filtered_solutions = []
        filtered_critiques = []
        
        for i, critique in enumerate(critiques):
            # Extract confidence score (simple regex - in practice, use more robust parsing)
            confidence_match = re.search(r'confidence.*?(\d+)', critique.lower())
            confidence = int(confidence_match.group(1)) if confidence_match else 50
            
            if confidence >= 70:
                filtered_solutions.append(solution_attempts[i])
                filtered_critiques.append(critique)

        # If no high-confidence solutions, trigger strategic pivot
        if len(filtered_solutions) == 0:
            # Reinterpret problem in new domain
            reinterpretation = await self.generate(
                instruction="""The initial approaches failed. Reinterpret this problem in a completely different mathematical domain.
                For example: If it seemed algebraic, consider a geometric interpretation. If it seemed combinatorial, consider a number-theoretic approach.
                Propose one radically different perspective and outline how it could lead to a solution.""",
                context=f"Original classification: {classification}\n\nFailed attempts: {' '.join(solution_attempts[:2])}"
            )
            
            # Generate new solution based on reinterpretation
            new_attempt = await self.generate(
                instruction=f"""Implement this new approach: {reinterpretation}
                
                Requirements:
                - Start from first principles
                - Be extra careful with assumptions
                - Show all work
                - Verify your answer satisfies all constraints""",
                context=""
            )
            
            filtered_solutions = [new_attempt]
            filtered_critiques = [await self.revise(
                instruction="Critique this solution attempt with extreme rigor. Look for any flaw, no matter how small.",
                context=new_attempt
            )]

        # STEP 5: SYNTHETIC ENSEMBLE - Combine insights from multiple solutions
        final_answer = await self.ensemble(
            instruction="""You are given multiple solution attempts and their critiques. Your task:
            1. Identify the most reliable answer from among the solutions
            2. If answers differ, determine which is correct by cross-validating with problem constraints
            3. If no solution is fully correct, synthesize a new answer by combining the strongest elements of each
            4. Extract any computational constraints (bounds, modular conditions, etc.) that can be used for verification
            5. Format your output as: "FINAL ANSWER: <integer>" followed by a brief justification""",
            contexts_list=[f"Solution: {sol}\n\nCritique: {crit}" for sol, crit in zip(filtered_solutions, filtered_critiques)]
        )

        # STEP 6: PROGRAMMATIC VERIFICATION - Use code to verify when possible
        # Extract the answer for verification
        answer_match = re.search(r'FINAL ANSWER:.*?(\d+)', final_answer)
        extracted_answer = answer_match.group(1) if answer_match else "0"

        # Create verification code based on problem type
        verification_code = await self.programmer(
            instruction=f"""Write Python code to verify that {extracted_answer} is indeed the correct answer to the original problem.
            The code should:
            - Implement the mathematical conditions from the problem
            - Check that the answer satisfies all constraints
            - Print "VERIFIED" if correct, "FAILED" if incorrect
            - Be as rigorous as possible
            
            If the problem is not computationally verifiable, print "NOT VERIFIABLE" and explain why.""",
            context=final_answer
        )

        # STEP 7: FINAL REFINEMENT - Produce competition-ready solution
        certified_solution = await self.revise(
            instruction="""Transform this into a competition-ready solution. Requirements:
            - Start with a clear statement of the answer
            - Follow with a concise, rigorous proof or derivation
            - Justify all non-trivial steps
            - Use proper mathematical notation
            - Ensure the answer is an integer between 000 and 999
            - Format for submission: box the final answer at the end
            
            This should be suitable for submission to a high-level math competition.""",
            context=f"Final answer: {final_answer}\n\nVerification: {verification_code}"
        )

        # Extract just the final answer in required format
        final_extraction = await self.generate(
            instruction="""Extract only the final numerical answer from the solution below. 
            The answer must be an integer between 000 and 999. 
            If multiple numbers appear, select the one that is clearly the final answer.
            Output only the 3-digit number (with leading zeros if necessary), nothing else.""",
            context=certified_solution
        )

        # Clean and return final answer
        # Remove any non-digit characters and ensure 3-digit format
        clean_answer = re.sub(r'\D', '', final_extraction)
        if len(clean_answer) == 0:
            clean_answer = "000"
        elif len(clean_answer) > 3:
            clean_answer = clean_answer[-3:]
        elif len(clean_answer) < 3:
            clean_answer = clean_answer.zfill(3)

        return clean_answer