# Workflow ID: drop_680_0
# Benchmark: drop
# Data Indices: [1368, 2893, 2698, 2621, 795]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify all field goal distances mentioned for the kicker in question.</instruction>
    <input>1</input>
    <output>field_goals</output>
  </node>
  <node id="3" type="agent">
    <instruction>Calculate the average of all field goals made by the kicker. Use the list of distances extracted in the previous step.</instruction>
    <input>2</input>
    <output>average_field_goal</output>
  </node>
  <node id="4" type="agent">
    <instruction>Determine the shortest field goal distance from the list of field goals.</instruction>
    <input>2</input>
    <output>shortest_field_goal</output>
  </node>
  <node id="5" type="agent">
    <instruction>Subtract the shortest field goal distance from the average field goal distance to find the difference.</instruction>
    <input>3,4</input>
    <output>difference</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
    <parameter>result</parameter>
  </node>