# Workflow ID: hotpotqa_285_0
# Benchmark: hotpotqa
# Data Indices: [581, 164, 24, 690]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the question. Focus on precise details that directly answer the query.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify the extracted information for consistency and relevance to the question. Eliminate any ambiguous or irrelevant data.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Apply logical reasoning to derive a clear conclusion based on verified information.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Provide the final answer in a concise and accurate format.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>