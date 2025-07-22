# Workflow ID: drop_341_0
# Benchmark: drop
# Data Indices: [2747, 1481, 1637, 728]

<agent id="1" type="extract">
    <instruction>Extract all quarterback names and their touchdown passes in the first half from the passage.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>Filter out only the first half touchdown passes for each quarterback.</instruction>
  </agent>
  <agent id="3" type="aggregate">
    <instruction>Aggregate total touchdowns per quarterback in the first half.</instruction>
  </agent>
  <agent id="4" type="compare">
    <instruction>Compare the total touchdowns between quarterbacks to determine who threw more in the first half.</instruction>
  </agent>
  <agent id="5" type="validate">
    <instruction>Validate that the comparison result is consistent with the extracted data and logical flow.</instruction>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>