# Workflow ID: drop_713_0
# Benchmark: drop
# Data Indices: [1520, 3159, 302, 3550]

<node id="1" type="input">
    <prompt>Understand the question and identify the key values needed for calculation.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract relevant numerical data from the passage that relates to the question.</prompt>
  </node>
  <node id="3" type="calculate">
    <prompt>Perform the necessary arithmetic or percentage calculation based on the extracted values.</prompt>
  </node>
  <node id="4" type="validate">
    <prompt>Verify that the calculation aligns with the context of the problem and makes logical sense.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Provide the final answer in the required format (e.g., number, percentage).</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>