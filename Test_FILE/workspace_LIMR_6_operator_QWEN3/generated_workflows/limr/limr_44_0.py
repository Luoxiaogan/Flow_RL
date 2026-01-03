# Workflow ID: limr_44_0
# Benchmark: limr
# Data Indices: [335, 277]

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

        # PHASE 1: PROBLEM CLASSIFICATION & CANONICALIZATION
        classification = await self.generate(
            instruction="""Perform deep problem classification and canonical transformation:
            1. Identify the primary mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            2. Detect any hidden structures (recursive sequences, telescoping sums, modular patterns, geometric symmetries)
            3. Rewrite the problem in its most tractable mathematical form (e.g., convert decimals to fractions, series to sigma notation)
            4. Extract all numerical constants, variables, and constraints
            5. Propose 2-3 candidate solution strategies ranked by expected efficiency
            Output format: Structured analysis with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION TRACK GENERATION
        # Spawn 3 independent solution approaches based on classification
        solution_tracks = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a rigorous algebraic/symbolic solution:
                Based on classification: {classification[:1000]}
                - Use exact symbolic manipulation (no floating point)
                - Show all transformation steps
                - Justify each mathematical operation
                - Derive final answer as integer between 000-999""",
                context=classification
            ),
            self.generate(
                instruction=f"""Develop a computational/numeric solution:
                Based on classification: {classification[:1000]}
                - Design precise algorithm avoiding floating-point errors
                - Handle edge cases and boundary conditions
                - Output must be exact integer
                - Include verification step""",
                context=classification
            ),
            self.generate(
                instruction=f"""Develop a combinatorial/geometric insight-based solution:
                Based on classification: {classification[:1000]}
                - Look for non-obvious patterns, symmetries, or transformations
                - Use mathematical induction, proof by contradiction, or generating functions if applicable
                - Connect to fundamental theorems or identities
                - Derive answer through logical necessity""",
                context=classification
            )
        )

        # PHASE 3: SELF-CRITIQUE & VALIDATION
        validated_tracks = []
        for i, track in enumerate(solution_tracks):
            critique = await self.generate(
                instruction=f"""Act as adversarial reviewer for Solution Track {i+1}:
                - Find logical gaps, calculation errors, or unjustified assumptions
                - Propose counterexamples or edge cases that might break the solution
                - If solution is robust, explain why it's watertight
                - If flawed, suggest specific corrections""",
                context=track
            )
            
            # Revise only if critique found issues
            if "error" in critique.lower() or "flaw" in critique.lower() or "gap" in critique.lower():
                revised = await self.revise(
                    instruction=f"""Incorporate critique and fix all identified issues:
                    Critique: {critique[:1500]}
                    - Address every concern raised
                    - Strengthen logical foundations
                    - Add missing verification steps
                    - Ensure final answer is exact integer 000-999""",
                    context=track
                )
                validated_tracks.append(revised)
            else:
                validated_tracks.append(track)  # Keep original if critique confirms robustness

        # PHASE 4: ANSWER EXTRACTION & CONSENSUS
        # Extract candidate answers from each track
        answer_extractions = await asyncio.gather(
            *[self.generate(
                instruction="""Extract the final numerical answer from this solution:
                - Must be integer between 000 and 999
                - If multiple answers, list all with confidence levels
                - If no clear answer, state 'UNCERTAIN'
                - Format: ONLY the number or 'UNCERTAIN'""",
                context=track
            ) for track in validated_tracks]
        )

        # Clean and validate extracted answers
        clean_answers = []
        for extraction in answer_extractions:
            # Extract first 3-digit number or mark uncertain
            match = re.search(r'\b([0-9]{1,3})\b', extraction)
            if match:
                num = int(match.group(1))
                if 0 <= num <= 999:
                    clean_answers.append(str(num).zfill(3))  # Pad to 3 digits
                else:
                    clean_answers.append("UNCERTAIN")
            else:
                clean_answers.append("UNCERTAIN")

        # If all tracks agree, return immediately
        if len(set(clean_answers)) == 1 and clean_answers[0] != "UNCERTAIN":
            return clean_answers[0]

        # Otherwise, synthesize with ensemble
        synthesis = await self.ensemble(
            instruction="""Synthesize multiple solution tracks into final answer:
            - Compare all solution approaches and extracted answers
            - Weight by robustness of reasoning and validation strength
            - Resolve conflicts by preferring solutions with watertight proofs
            - If still uncertain, propose most mathematically justified answer
            - Final output MUST be integer 000-999""",
            contexts_list=[f"Track {i+1} Answer: {ans}\nSolution: {track[:500]}" 
                          for i, (ans, track) in enumerate(zip(clean_answers, validated_tracks))]
        )

        # Final extraction and formatting
        final_answer = await self.generate(
            instruction="""Extract final integer answer from synthesis:
            - Must be between 000 and 999
            - Remove all explanatory text
            - Output ONLY the 3-digit number (pad with leading zeros if needed)""",
            context=synthesis
        )

        # Ensure proper formatting
        match = re.search(r'\b([0-9]{1,3})\b', final_answer)
        if match:
            return str(int(match.group(1))).zfill(3)
        else:
            # Fallback: return first track's answer if all else fails
            return clean_answers[0] if clean_answers[0] != "UNCERTAIN" else "000"