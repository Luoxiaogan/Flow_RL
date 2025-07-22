# Workflow ID: hotpotqa_563_0
# Benchmark: hotpotqa
# Data Indices: [1436, 1148, 2573, 2941, 424]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the context related to the key entities. Focus on precise details that directly answer the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted information matches the question's requirements. Eliminate irrelevant or ambiguous data.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Construct a clear and concise answer based on verified information. Ensure it directly addresses the question without extra detail.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Finalize and return the answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>