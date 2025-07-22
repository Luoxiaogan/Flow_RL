# Workflow ID: drop_249_0
# Benchmark: drop
# Data Indices: [3314, 1795, 594, 1289, 1626]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key elements in the passage relevant to the question. Break down the question into smaller sub-questions if needed.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Extract numerical values or specific details from the passage that directly answer the sub-questions identified in node 2.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Perform necessary calculations or comparisons using the extracted values to derive intermediate results.</instruction>
  </node>
  <node id="5" type="agent">
    <instruction>Verify that each step logically leads to the final answer, ensuring no information is lost or misinterpreted.</instruction>
  </node>
  <node id="6" type="output">
    <description>Return the final answer based on all prior steps.</description>
  </node>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>