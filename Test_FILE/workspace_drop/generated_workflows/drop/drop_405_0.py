# Workflow ID: drop_405_0
# Benchmark: drop
# Data Indices: [873, 2600, 808, 2935, 1499]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical question in the passage and locate the relevant sentence that answers it. Think step by step: first, determine what is being asked; second, scan for the specific value or event related to the question; third, extract only the number or value that directly answers the question.</instruction>
    <input>problem</input>
    <output>answer</output>
  </node>
  <node id="3" type="agent">
    <instruction>Verify the extracted answer by cross-referencing with other parts of the passage. If multiple values are mentioned, ensure the correct one is selected based on context. If no clear answer exists, return "No clear answer found".</instruction>
    <input>answer</input>
    <output>verified_answer</output>
  </node>
  <node id="4" type="output">
    <input>verified_answer</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>