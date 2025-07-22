# Workflow ID: hotpotqa_273_0
# Benchmark: hotpotqa
# Data Indices: [3373, 3520, 3087, 1673]

<operator id="0">
    <instruction>Identify the key entities in the question and context that are directly relevant to answering the query. Focus on extracting precise information without overcomplicating the task.</instruction>
    <input>problem</input>
    <output>filtered_entities</output>
  </operator>
  <operator id="1">
    <instruction>For each entity, determine if it matches a known fact or can be logically inferred from the context provided. Prioritize direct matches over indirect ones.</instruction>
    <input>filtered_entities</input>
    <output>candidate_answers</output>
  </operator>
  <operator id="2">
    <instruction>Validate each candidate answer by cross-referencing with multiple context entries to ensure consistency and eliminate false positives.</instruction>
    <input>candidate_answers</input>
    <output>validated_answers</output>
  </operator>
  <operator id="3">
    <instruction>Among the validated answers, select the one that best satisfies the original question based on clarity, specificity, and relevance.</instruction>
    <input>validated_answers</input>
    <output>final_answer</output>
  </operator>
  <operator id="4">
    <instruction>Ensure the final answer aligns with the question's intent and does not introduce any ambiguity or incorrect interpretation.</instruction>
    <input>final_answer</input>
    <output>verified_final_answer</output>
  </operator>
  <operator id="5">
    <instruction>Generate a concise explanation for why this answer is correct based on the reasoning steps taken through previous operators.</instruction>
    <input>verified_final_answer</input>
    <output>explanation</output>
  </operator>
  <operator id="6">
    <instruction>Combine the final answer and explanation into a single structured output for clarity and completeness.</instruction>
    <input>verified_final_answer, explanation</input>
    <output>result</output>
  </operator>