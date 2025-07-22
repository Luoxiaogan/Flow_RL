# Workflow ID: hotpotqa_126_0
# Benchmark: hotpotqa
# Data Indices: [3371, 901, 668, 41]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities. Focus on direct matches or clear associations.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted information directly answers the question without ambiguity.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Check for any additional context that may support or contradict the answer.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on verified information.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>