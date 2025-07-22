# Workflow ID: hotpotqa_397_0
# Benchmark: hotpotqa
# Data Indices: [1333, 678, 3329, 3378]

<operator id="1" type="agent">
    <instruction>Identify the key entities in the problem and determine the specific question being asked. Break down the problem into its core components for clarity.</instruction>
    <input>problem</input>
    <output>core_entities_and_question</output>
  </operator>

  <operator id="2" type="agent">
    <instruction>Extract relevant contextual clues from the provided text that directly relate to the core question. Focus only on information that can help identify the correct answer.</instruction>
    <input>core_entities_and_question, context</input>
    <output>relevant_clues</output>
  </operator>

  <operator id="3" type="agent">
    <instruction>Apply logical reasoning to connect the relevant clues with known facts or patterns. Eliminate any irrelevant data and narrow down possible answers based on evidence.</instruction>
    <input>relevant_clues</input>
    <output>filtered_candidates</output>
  </operator>

  <operator id="4" type="agent">
    <instruction>Verify each candidate against the full context to ensure consistency and accuracy. Discard any options that contradict established facts or lack sufficient support.</instruction>
    <input>filtered_candidates, context</input>
    <output>verified_answer</output>
  </operator>

  <operator id="5" type="agent">
    <instruction>Double-check the final answer by cross-referencing it with all available evidence. Ensure no step was skipped and the conclusion is logically sound.</instruction>
    <input>verified_answer, context</input>
    <output>final_output</output>
  </operator>

  <operator id="6" type="agent">
    <instruction>Return the verified answer as the solution to the original question. Confirm that the output matches the required format and addresses the problem precisely.</instruction>
    <input>final_output</input>
    <output>answer</output>
  </operator>