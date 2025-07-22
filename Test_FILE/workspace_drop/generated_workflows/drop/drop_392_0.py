# Workflow ID: drop_392_0
# Benchmark: drop
# Data Indices: [1374, 356, 151, 898]

<node id="1">
    <instruction>Identify all field goals mentioned in the passage and extract their yardages.</instruction>
    <output>list_of_field_goals</output>
  </node>
  <node id="2">
    <instruction>Calculate the difference between the first and second field goals from the list.</instruction>
    <input>list_of_field_goals</input>
    <output>yard_difference</output>
  </node>
  <node id="3">
    <instruction>Return the calculated yard difference as the final answer.</instruction>
    <input>yard_difference</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>