# Workflow ID: drop_145_0
# Benchmark: drop
# Data Indices: [3074, 2358, 2300, 2791, 1667]

<start/>
  <agent id="1" type="extract">
    <instruction>Extract all scoring plays from the passage, noting the type of play and yardage.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>Filter out non-scoring plays and focus only on touchdowns and field goals.</instruction>
  </agent>
  <agent id="3" type="compare">
    <instruction>Compare all scored plays to identify the longest one by yardage.</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Validate that the identified longest play is indeed the maximum yardage among all scoring plays.</instruction>
  </agent>
  <agent id="5" type="aggregate">
    <instruction>Aggregate the result from the validation step to produce the final answer.</instruction>
  </agent>
  <end/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="end"/>