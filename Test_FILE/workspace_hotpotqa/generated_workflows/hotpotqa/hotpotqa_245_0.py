# Workflow ID: hotpotqa_245_0
# Benchmark: hotpotqa
# Data Indices: [1686, 3045, 229, 3688]

<agent id="1">
    <instruction>Identify the key events mentioned in the question and extract the relevant year from the context.</instruction>
    <input>problem</input>
    <output>year_candidate</output>
  </agent>
  <agent id="2">
    <instruction>Verify that the extracted year matches both the Seven Days Battles and Second Battle of Bull Run by cross-referencing with the context.</instruction>
    <input>year_candidate</input>
    <output>verification_result</output>
  </agent>
  <agent id="3">
    <instruction>Ensure the verification result confirms a single consistent year for both battles, and return it as the final answer.</instruction>
    <input>verification_result</input>
    <output>final_answer</output>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>