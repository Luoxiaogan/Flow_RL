# Workflow ID: hotpotqa_82_0
# Benchmark: hotpotqa
# Data Indices: [3853, 1239, 227, 1398]

<node id="1" type="input">
    <prompt>Understand the problem and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the main subject and relevant context from the provided information. Think step by step to isolate the core question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Search for direct connections between the subject and possible answers in the context. Use logical deduction to eliminate irrelevant options.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the consistency of the answer with all contextual clues, especially dates, names, or roles that must align exactly.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on verified evidence from the context.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>