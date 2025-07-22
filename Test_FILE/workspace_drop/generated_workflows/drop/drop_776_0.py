# Workflow ID: drop_776_0
# Benchmark: drop
# Data Indices: [1153, 1492, 2999, 3342]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data relevant to the question in the passage.</instruction>
    <input>1</input>
    <output>key_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary arithmetic or percentage calculations based on the key data.</instruction>
    <input>2</input>
    <output>calculation_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the calculation aligns with the question's requirement and ensures no information loss.</instruction>
    <input>3</input>
    <output>verified_result</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>