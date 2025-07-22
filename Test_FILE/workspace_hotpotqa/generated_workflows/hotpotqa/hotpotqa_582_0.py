# Workflow ID: hotpotqa_582_0
# Benchmark: hotpotqa
# Data Indices: [3988, 1656, 937, 2794]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities mentioned.</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>Extract relevant context from the provided text for the key entities. Focus on the specific details related to the question.</prompt>
  </node>
  
  <node id="3" type="agent">
    <prompt>Verify the extracted information against the context to ensure accuracy and relevance.</prompt>
  </node>
  
  <node id="4" type="agent">
    <prompt>Formulate a clear answer based on the verified information, ensuring it directly addresses the question.</prompt>
  </node>
  
  <node id="5" type="output">
    <prompt>Return the final answer as a concise statement that resolves the question.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>