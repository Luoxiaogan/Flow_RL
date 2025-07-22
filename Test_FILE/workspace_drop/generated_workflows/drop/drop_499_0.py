# Workflow ID: drop_499_0
# Benchmark: drop
# Data Indices: [2494, 1232, 2517, 1068, 1434]

<node id="1">
    <instruction>Extract key numerical data from the passage relevant to the question.</instruction>
    <output>numerical_data</output>
  </node>
  <node id="2">
    <instruction>Identify the specific entity mentioned in the question (e.g., player, group, religion).</instruction>
    <output>entity</output>
  </node>
  <node id="3">
    <instruction>Match the entity with the corresponding numerical value or event in the passage.</instruction>
    <output>match_result</output>
  </node>
  <node id="4">
    <instruction>Compare values if necessary (e.g., gender ratio, field goal count) to determine the answer.</instruction>
    <output>comparison_result</output>
  </node>
  <node id="5">
    <instruction>Validate the result against the context of the question to ensure correctness.</instruction>
    <output>final_answer</output>
  </node>
  <edge from="1" to="3"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>