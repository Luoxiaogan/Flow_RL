# Workflow ID: drop_604_0
# Benchmark: drop
# Data Indices: [1159, 2075, 2968, 2669, 3224]

<node id="1">
    <instruction>Understand the question and identify key information needed to solve it.</instruction>
    <next>2</next>
  </node>
  <node id="2">
    <instruction>Locate the relevant passage segment that addresses the question.</instruction>
    <next>3</next>
  </node>
  <node id="3">
    <instruction>Extract specific details from the passage that directly answer the question.</instruction>
    <next>4</next>
  </node>
  <node id="4">
    <instruction>Verify that the extracted data matches what is asked in the question.</instruction>
    <next>5</next>
  </node>
  <node id="5">
    <instruction>Formulate a clear and concise answer based on the verified data.</instruction>
    <next>6</next>
  </node>
  <node id="6">
    <instruction>Double-check for any inconsistencies or missing information in the reasoning chain.</instruction>
    <next>7</next>
  </node>
  <node id="7">
    <instruction>Return the final answer as the output of this graph.</instruction>
    <next>end</next>
  </node>