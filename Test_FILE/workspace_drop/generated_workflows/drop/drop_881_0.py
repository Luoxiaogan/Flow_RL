# Workflow ID: drop_881_0
# Benchmark: drop
# Data Indices: [1774, 424, 3769, 1519, 3223]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the relevant passage segment that contains the answer to the question.</instruction>
    <input>problem</input>
    <output>relevant_passage</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify and isolate the specific numerical value mentioned in the passage related to the question.</instruction>
    <input>relevant_passage</input>
    <output>numerical_value</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the extracted number matches the context of the question—ensure it refers to the correct event or statistic.</instruction>
    <input>numerical_value</input>
    <output>validated_answer</output>
  </node>
  <node id="5" type="output">
    <input>validated_answer</input>
  </node>