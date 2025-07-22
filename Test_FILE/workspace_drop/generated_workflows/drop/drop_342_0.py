# Workflow ID: drop_342_0
# Benchmark: drop
# Data Indices: [3481, 2764, 362, 1855]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify the key information related to the question.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant details from the passage that directly answer the question. Think step by step: What is being asked? What part of the passage contains the answer?</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted information matches the question's requirements. If not, recheck the passage for missing or misinterpreted data.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Formulate a clear and concise answer based on the verified information. Ensure it directly addresses the question without extra details.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer as a single value or short phrase that precisely answers the question.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>