# Workflow ID: drop_679_0
# Benchmark: drop
# Data Indices: [3355, 2174, 1376, 2461, 2756]

<node id="start" type="input">
    <prompt>Understand the question and identify key data points needed to solve it.</prompt>
  </node>
  
  <node id="extract" type="agent">
    <prompt>Extract relevant numerical values or conditions from the passage based on the question.</prompt>
    <depends>start</depends>
  </node>
  
  <node id="process" type="agent">
    <prompt>Apply mathematical operations or logical comparisons to the extracted data to answer the question.</prompt>
    <depends>extract</depends>
  </node>
  
  <node id="validate" type="agent">
    <prompt>Verify that the computed result aligns with the passage details and makes logical sense.</prompt>
    <depends>process</depends>
  </node>
  
  <node id="output" type="output">
    <prompt>Return the final answer in a clear and concise format.</prompt>
    <depends>validate</depends>
  </node>