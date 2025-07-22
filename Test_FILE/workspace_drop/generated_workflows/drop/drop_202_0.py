# Workflow ID: drop_202_0
# Benchmark: drop
# Data Indices: [2270, 2301, 115, 1351, 3568]

<node id="1" type="input">
    <prompt>Extract the relevant numerical information from the passage related to the question.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Identify all instances of field goals with a distance of 31 yards mentioned in the passage.</prompt>
  </node>
  <node id="3" type="filter">
    <prompt>Filter out any non-31-yard field goals or irrelevant events (e.g., touchdowns, fumbles).</prompt>
  </node>
  <node id="4" type="count">
    <prompt>Count the total number of 31-yard field goals explicitly described in the filtered results.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the count as the final answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>