# Workflow ID: drop_125_0
# Benchmark: drop
# Data Indices: [1682, 2186, 1859, 2800]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract all field goal distances from the passage. Identify the longest and shortest values.</instruction>
    <param name="data">1</param>
    <output>field_goal_distances</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Calculate the difference between the longest and shortest field goal distances.</instruction>
    <param name="data">2</param>
    <output>difference</output>
  </node>
  
  <node id="4" type="output">
    <param name="result">3</param>
  </node>