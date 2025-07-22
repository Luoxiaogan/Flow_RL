# Workflow ID: drop_129_0
# Benchmark: drop
# Data Indices: [1526, 3808, 487, 450]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to age groups.</instruction>
    <output>age_group_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the percentages of the two specified age groups: 25-44 and 45-64.</instruction>
    <output>comparison_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Determine which age group is larger based on the comparison result.</instruction>
    <output>larger_age_group</output>
  </node>
  <node id="5" type="output">
    <data>larger_age_group</data>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>