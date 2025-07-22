# Workflow ID: drop_477_0
# Benchmark: drop
# Data Indices: [2258, 2740, 2759, 3182]

<node id="1" type="input">
    <param>problem</param>
  </node>
  
  <node id="2" type="agent">
    <instruction>
      Analyze the passage to identify all field goals mentioned in the third and fourth quarters.
    </instruction>
    <output>field_goals</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>
      From the list of field goals, determine the shortest yardage by comparing each value.
    </instruction>
    <output>shortest_field_goal</output>
  </node>
  
  <node id="4" type="output">
    <param>shortest_field_goal</param>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>