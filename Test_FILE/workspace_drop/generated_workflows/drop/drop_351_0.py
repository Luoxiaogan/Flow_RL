# Workflow ID: drop_351_0
# Benchmark: drop
# Data Indices: [2784, 468, 3215, 17, 719]

<node id="1">
    <instruction>Extract all touchdown pass distances from the passage.</instruction>
    <output>list_of_touchdowns</output>
  </node>
  <node id="2">
    <instruction>Identify the shortest touchdown distance from the list.</instruction>
    <input>list_of_touchdowns</input>
    <output>shortest_touchdown</output>
  </node>
  <node id="3">
    <instruction>Return the value of the shortest touchdown distance.</instruction>
    <input>shortest_touchdown</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>