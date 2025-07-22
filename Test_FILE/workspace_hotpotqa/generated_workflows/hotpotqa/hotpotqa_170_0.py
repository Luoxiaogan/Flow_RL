# Workflow ID: hotpotqa_170_0
# Benchmark: hotpotqa
# Data Indices: [1978, 3084, 2867, 764]

<agent id="1" type="extract">
    <instruction>Identify the key entities and their attributes from the context provided.</instruction>
  </agent>
  <agent id="2" type="compare">
    <instruction>Compare the values of the attributes to determine which entity meets the criteria in the question.</instruction>
  </agent>
  <agent id="3" type="validate">
    <instruction>Verify the correctness of the comparison by cross-referencing with all relevant data points.</instruction>
  </agent>
  <agent id="4" type="synthesize">
    <instruction>Combine the validated results into a coherent final answer that directly addresses the question.</instruction>
  </agent>
  <link from="1" to="2"/>
  <link from="2" to="3"/>
  <link from="3" to="4"/>