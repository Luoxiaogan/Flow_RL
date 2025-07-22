# Workflow ID: hotpotqa_99_0
# Benchmark: hotpotqa
# Data Indices: [2098, 3334, 3544, 2465, 3217]

<operator id="0">
    <instruction>Identify the key entities in the problem and their relationships. Break down the question into smaller, answerable components.</instruction>
    <input>problem</input>
    <output>structured_query</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant facts from the context that directly address each component of the structured query.</instruction>
    <input>structured_query, context</input>
    <output>evidence_set</output>
  </operator>
  <operator id="2">
    <instruction>Validate each piece of evidence for accuracy and relevance to the original question. Discard irrelevant or conflicting information.</instruction>
    <input>evidence_set</input>
    <output>validated_evidence</output>
  </operator>
  <operator id="3">
    <instruction>Construct a logical chain from validated evidence to derive the final answer. Ensure no step skips essential reasoning.</instruction>
    <input>validated_evidence</input>
    <output>final_answer</output>
  </operator>
  <operator id="4">
    <instruction>Double-check the final answer against the original question to ensure it fully addresses the query without ambiguity.</instruction>
    <input>final_answer, problem</input>
    <output>verified_answer</output>
  </operator>