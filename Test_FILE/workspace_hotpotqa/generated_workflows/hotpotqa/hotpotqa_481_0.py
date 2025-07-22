# Workflow ID: hotpotqa_481_0
# Benchmark: hotpotqa
# Data Indices: [3169, 2433, 3628, 1791, 3985]

<agent id="1" type="extract">
    <instruction>Extract key entities and facts from the context relevant to the question.</instruction>
  </agent>
  <agent id="2" type="reason">
    <instruction>Reason step-by-step using extracted entities to identify the correct answer.</instruction>
  </agent>
  <agent id="3" type="validate">
    <instruction>Validate the reasoning by cross-checking with the context for accuracy.</instruction>
  </agent>
  <agent id="4" type="optimize">
    <instruction>Optimize the solution path by removing redundant steps or clarifying ambiguous logic.</instruction>
  </agent>
  <agent id="5" type="output">
    <instruction>Generate the final answer based on validated and optimized reasoning.</instruction>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>