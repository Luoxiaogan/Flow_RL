# Workflow ID: drop_636_0
# Benchmark: drop
# Data Indices: [1339, 2943, 13, 3742, 2373]

<start/>
  <agent id="1" type="extract">
    <instruction>Extract all field goal distances from the passage and identify which ones are over 30 yards.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>Filter field goals to only include those over 30 yards.</instruction>
  </agent>
  <agent id="3" type="count">
    <instruction>Count the number of filtered field goals.</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Verify that the count is correct by cross-checking with the passage's timeline for fourth quarter only.</instruction>
  </agent>
  <agent id="5" type="output">
    <instruction>Return the final count as the answer to the question.</instruction>
  </agent>
  <end/>
  <edge from="start" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="end"/>