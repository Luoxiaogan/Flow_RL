# Workflow ID: drop_719_0
# Benchmark: drop
# Data Indices: [387, 623, 3091, 3869, 999]

<node id="1">
    <task>Extract relevant numerical data from passage</task>
    <input>problem</input>
    <output>raw_data</output>
  </node>
  <node id="2">
    <task>Identify the key comparison or count required by the question</task>
    <input>raw_data, question</input>
    <output>comparison_logic</output>
  </node>
  <node id="3">
    <task>Apply logical reasoning to compute the answer</task>
    <input>comparison_logic</input>
    <output>answer</output>
  </node>
  <node id="4">
    <task>Validate the answer against the passage context</task>
    <input>answer, raw_data</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>