# Workflow ID: drop_444_0
# Benchmark: drop
# Data Indices: [614, 1685, 176, 2480]

<node id="1">
    <instruction>Identify the relevant data points from the passage that pertain to the question.</instruction>
    <agent>extractor</agent>
  </node>
  <node id="2">
    <instruction>Process the extracted data to isolate the values needed for calculation (e.g., longest and shortest field goals).</instruction>
    <agent>processor</agent>
  </node>
  <node id="3">
    <instruction>Calculate the difference between the longest and shortest field goals.</instruction>
    <agent>calculator</agent>
  </node>
  <node id="4">
    <instruction>Validate the result by cross-checking with original passage values.</instruction>
    <agent>verifier</agent>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>