# Workflow ID: drop_206_0
# Benchmark: drop
# Data Indices: [2672, 283, 2293, 891, 3703]

<node id="start" type="input">
    <prompt>Understand the question and identify key entities or values to compare.</prompt>
  </node>
  
  <node id="agent1" type="agent">
    <prompt>Identify the relevant data in the passage related to the question. Extract numerical values or player names as needed.</prompt>
  </node>
  
  <node id="agent2" type="agent">
    <prompt>Compare the extracted values step by step to determine the correct answer based on the question.</prompt>
  </node>
  
  <node id="agent3" type="agent">
    <prompt>Verify that the comparison logic aligns with the question's requirement—e.g., who threw more TDs, how many points, etc.</prompt>
  </node>
  
  <node id="output" type="output">
    <prompt>Return the final answer derived from the agents' analysis.</prompt>
  </node>
  
  <edge from="start" to="agent1"/>
  <edge from="agent1" to="agent2"/>
  <edge from="agent2" to="agent3"/>
  <edge from="agent3" to="output"/>