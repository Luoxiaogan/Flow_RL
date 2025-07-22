# Workflow ID: drop_46_0
# Benchmark: drop
# Data Indices: [3177, 2216, 3479, 3268]

<node id="1" type="input">
    <prompt>Extract the relevant numerical data from the passage related to the question.</prompt>
  </node>
  
  <node id="2" type="process">
    <prompt>Identify the key players and their actions mentioned in relation to scoring or yardage.</prompt>
  </node>
  
  <node id="3" type="process">
    <prompt>Determine which player threw the longest touchdown pass based on the yardage of each touchdown pass mentioned.</prompt>
  </node>
  
  <node id="4" type="process">
    <prompt>Compare all touchdown passes to find the maximum yardage value.</prompt>
  </node>
  
  <node id="5" type="output">
    <prompt>Return the yardage of the longest touchdown pass as the final answer.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>