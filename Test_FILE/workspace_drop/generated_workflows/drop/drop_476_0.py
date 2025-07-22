# Workflow ID: drop_476_0
# Benchmark: drop
# Data Indices: [3676, 1653, 777, 1397, 2112]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract all field goal events from the passage. Identify which team scored each field goal and the quarter in which it occurred.</instruction>
    <input>1</input>
    <output>field_goals</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Filter field goals to only those that occurred in the third quarter.</instruction>
    <input>2</input>
    <output>third_quarter_field_goals</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Count the number of field goals made by each team in the third quarter.</instruction>
    <input>3</input>
    <output>counts</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Determine the number of field goals kicked by the Bears in the third quarter based on the counts.</instruction>
    <input>4</input>
    <output>result</output>
  </node>
  
  <node id="6" type="output">
    <input>5</input>
  </node>