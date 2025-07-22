# Workflow ID: drop_533_0
# Benchmark: drop
# Data Indices: [2361, 1819, 656, 3704]

<operator id="0">
    <instruction>Understand the question and identify key entities or quantities to extract from the passage.</instruction>
    <input>problem</input>
    <output>question_analysis</output>
  </operator>
  <operator id="1">
    <instruction>Scan the passage for explicit mentions of the key entities or quantities identified in the question analysis.</instruction>
    <input>question_analysis, passage</input>
    <output>raw_answer_candidates</output>
  </operator>
  <operator id="2">
    <instruction>Filter and validate candidates based on context—ensure they directly answer the question without ambiguity.</instruction>
    <input>raw_answer_candidates</input>
    <output>validated_answer</output>
  </operator>
  <operator id="3">
    <instruction>Format the validated answer into a clear, concise response that matches the question's structure.</instruction>
    <input>validated_answer</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>