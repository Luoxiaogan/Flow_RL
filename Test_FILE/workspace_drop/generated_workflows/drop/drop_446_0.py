# Workflow ID: drop_446_0
# Benchmark: drop
# Data Indices: [226, 661, 3360, 3332]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical value related to the question in the passage.</instruction>
    <input>1</input>
    <output>key_value</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract any comparative or percentage-based data relevant to the question.</instruction>
    <input>1</input>
    <output>comparison_data</output>
  </node>
  <node id="4" type="agent">
    <instruction>Calculate the difference or ratio between the extracted values if needed.</instruction>
    <input>2,3</input>
    <output>result</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>