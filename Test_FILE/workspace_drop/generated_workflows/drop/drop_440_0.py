# Workflow ID: drop_440_0
# Benchmark: drop
# Data Indices: [389, 953, 2078, 3534]

<node id="1" type="input">
    <prompt>Extract the key dates from the passage related to Zelaya's resignation and Madriz's election.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Calculate the number of days between Zelaya's resignation on December 14, 1909, and Madriz's election on December 20, 1909.</prompt>
  </node>
  <node id="3" type="output">
    <prompt>Return the computed number of days as the final answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>