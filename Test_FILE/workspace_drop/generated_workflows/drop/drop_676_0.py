# Workflow ID: drop_676_0
# Benchmark: drop
# Data Indices: [725, 1265, 484, 643, 646]

<node id="1">
    <task>Extract relevant numerical data from passage</task>
    <input>problem</input>
    <output>list_of_values</output>
  </node>
  <node id="2">
    <task>Identify the field goals and their yardages for the kicker in question</task>
    <input>list_of_values</input>
    <output>field_goal_yards</output>
  </node>
  <node id="3">
    <task>Calculate the difference between the second and first field goal yardages</task>
    <input>field_goal_yards</input>
    <output>yardage_difference</output>
  </node>
  <node id="4">
    <task>Return the computed difference as the final answer</task>
    <input>yardage_difference</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>