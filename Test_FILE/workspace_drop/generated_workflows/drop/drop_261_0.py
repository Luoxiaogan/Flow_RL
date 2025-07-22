# Workflow ID: drop_261_0
# Benchmark: drop
# Data Indices: [438, 2096, 135, 275, 1618]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify the key information related to the question.</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>Extract the relevant details from the passage that directly answer the question. Think step by step: First, locate the part of the passage mentioning the subject of the question. Then, find the specific detail that answers what is being asked.</prompt>
  </node>
  
  <node id="3" type="agent">
    <prompt>Verify if the extracted detail matches exactly with what the question asks. If not, recheck the passage for any other possible references. Ensure no ambiguity remains in the answer.</prompt>
  </node>
  
  <node id="4" type="output">
    <prompt>Provide the final answer based on the verified detail. Do not include any extra explanation unless explicitly required.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>