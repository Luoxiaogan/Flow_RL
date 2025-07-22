# Workflow ID: drop_829_0
# Benchmark: drop
# Data Indices: [3165, 2788, 2219, 1194]

<agent id="1" type="extract">
    <instruction>Extract all scoring events from the passage, noting the type of score (touchdown, field goal), yardage, and team involved.</instruction>
  </agent>
  
  <agent id="2" type="filter">
    <instruction>Filter the extracted scores to only include those made by a specific player or team based on the question.</instruction>
  </agent>
  
  <agent id="3" type="aggregate">
    <instruction>Aggregate the filtered scores to compute the total yards for the specified scorer, if applicable.</instruction>
  </agent>
  
  <agent id="4" type="validate">
    <instruction>Verify that the computed total matches the context of the question and ensures no data loss occurred during filtering or aggregation.</instruction>
  </agent>
  
  <agent id="5" type="format">
    <instruction>Format the final result as a numeric answer with no additional text or explanation.</instruction>
  </agent>
  
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>