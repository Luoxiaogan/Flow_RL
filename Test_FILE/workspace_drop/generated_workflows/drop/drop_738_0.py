# Workflow ID: drop_738_0
# Benchmark: drop
# Data Indices: [3427, 2535, 1297, 429, 254]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the relevant numerical data in the passage that pertains to the question. Extract all field goal distances mentioned.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Sum all the field goal distances attributed to the player in question, ensuring only valid entries are included.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <param name="result">The total yards from field goals kicked by the specified player.</param>
    <depends_on>3</depends_on>
  </node>