# Workflow ID: drop_850_0
# Benchmark: drop
# Data Indices: [3630, 2678, 1665, 2730]

<node id="1" type="input">
    <prompt>Understand the question and extract key information from the passage.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Identify relevant data points that directly answer the question.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Apply mathematical or logical operations to derive the required value.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Present the final answer clearly based on the derived result.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>