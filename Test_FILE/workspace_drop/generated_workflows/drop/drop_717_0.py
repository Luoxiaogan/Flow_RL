# Workflow ID: drop_717_0
# Benchmark: drop
# Data Indices: [1362, 1852, 3783, 2591, 3453]

<node id="1" type="input">
    <prompt>Extract all field goals and their yardages from the passage.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Identify the longest field goal for each kicker mentioned in the passage.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Identify the second longest field goal for each kicker mentioned in the passage.</prompt>
  </node>
  <node id="4" type="compute">
    <prompt>Calculate the difference between Aker's second longest and Cundiff's second longest field goals.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the numerical difference in yards.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>