# Workflow ID: drop_34_0
# Benchmark: drop
# Data Indices: [916, 3872, 1151, 2376]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the relevant field goal distances from the passage. Identify Joe Nedney's field goal distance and Josh Brown's longest field goal distance.</instruction>
    <input>1</input>
    <output>field_goal_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Calculate the difference in yards between Joe Nedney's field goal and Josh Brown's longest field goal. Ensure the calculation is accurate by subtracting the smaller value from the larger one.</instruction>
    <input>2</input>
    <output>yard_difference</output>
  </node>
  <node id="4" type="output">
    <input>3</input>
    <output>final_answer</output>
  </node>