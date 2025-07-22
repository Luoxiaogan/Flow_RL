# Workflow ID: drop_395_0
# Benchmark: drop
# Data Indices: [184, 3625, 1099, 3304, 1402]

<node id="1" type="input">
    <prompt>Extract all touchdown pass yardages from the passage.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Identify and list all touchdown pass distances mentioned in the text.</prompt>
  </node>
  <node id="3" type="filter">
    <prompt>Filter out only the touchdown pass values (exclude runs, field goals, etc.).</prompt>
  </node>
  <node id="4" type="transform">
    <prompt>Convert the list of yardages into integers for comparison.</prompt>
  </node>
  <node id="5" type="aggregate">
    <prompt>Find the minimum value from the list of touchdown pass yardages.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the shortest touchdown pass distance as the final answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>