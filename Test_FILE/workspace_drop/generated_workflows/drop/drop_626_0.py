# Workflow ID: drop_626_0
# Benchmark: drop
# Data Indices: [265, 1964, 1642, 325, 3393]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to households and gender.</instruction>
    <input>1</input>
    <output>household_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Calculate the difference between total households and those headed by males.</instruction>
    <input>2</input>
    <output>difference</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the calculation logic: total households minus male-headed households equals female-headed households.</instruction>
    <input>2</input>
    <output>verification</output>
  </node>
  <node id="5" type="agent">
    <instruction>Ensure the final answer is correctly formatted as an integer representing the difference in household counts.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  <node id="6" type="output">
    <data>final_answer</data>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="5"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>