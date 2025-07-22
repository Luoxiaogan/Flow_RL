# Workflow ID: hotpotqa_69_0
# Benchmark: hotpotqa
# Data Indices: [2380, 2016, 761, 2717]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the question. Focus on direct matches or logical connections.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted information directly answers the question without ambiguity.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Ensure no external assumptions are made; only use provided context.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on verified information.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>