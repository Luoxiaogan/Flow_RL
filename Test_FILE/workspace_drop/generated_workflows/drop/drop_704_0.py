# Workflow ID: drop_704_0
# Benchmark: drop
# Data Indices: [1471, 1854, 2060, 2586]

<node id="1" type="input">
    <prompt>Understand the question and identify the key information needed to answer it.</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>Extract all passing touchdown plays from the passage. Focus only on the yardage of each touchdown pass.</prompt>
    <output>list of passing touchdowns with yardages</output>
  </node>
  
  <node id="3" type="agent">
    <prompt>Filter out only the passing touchdowns (not runs or field goals) and their respective yardages.</prompt>
    <output>filtered list of passing touchdowns</output>
  </node>
  
  <node id="4" type="agent">
    <prompt>Find the maximum value in the filtered list of passing touchdown yardages.</prompt>
    <output>longest passing touchdown yardage</output>
  </node>
  
  <node id="5" type="output">
    <prompt>Return the longest passing touchdown yardage as the final answer.</prompt>
    <input>longest passing touchdown yardage</input>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>