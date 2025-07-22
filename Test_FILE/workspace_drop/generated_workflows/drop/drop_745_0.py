# Workflow ID: drop_745_0
# Benchmark: drop
# Data Indices: [1261, 3335, 954, 1771]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key information related to the question in the passage. Break down the problem step by step to locate relevant data points.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract all instances of touchdown passes mentioned in the passage, noting the passer and receiver for each.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Sum the yardage of all touchdown passes identified in the previous step to compute the total yards.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>