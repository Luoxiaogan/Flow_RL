# Workflow ID: drop_712_0
# Benchmark: drop
# Data Indices: [1494, 84, 3326, 72]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify all relevant numerical values related to the question.</prompt>
  </node>
  
  <node id="2" type="filter">
    <prompt>Extract only the yardage values associated with scoring plays or field goal attempts based on the question.</prompt>
  </node>
  
  <node id="3" type="compare">
    <prompt>Determine the maximum value among the extracted yardages to find the longest play or field goal attempt.</prompt>
  </node>
  
  <node id="4" type="output">
    <prompt>Return the highest yardage value as the answer to the question.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>