# Workflow ID: hotpotqa_402_0
# Benchmark: hotpotqa
# Data Indices: [3298, 1457, 82, 2464]

<start/>
  <node id="1" type="agent">
    <instruction>Think step by step to identify the relevant information from the context that answers the question.</instruction>
    <input>problem</input>
    <output>filtered_context</output>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the key details such as names, dates, and relationships that are directly relevant to the question.</instruction>
    <input>filtered_context</input>
    <output>key_details</output>
  </node>
  <node id="3" type="agent">
    <instruction>Use logical reasoning to connect the extracted details and determine the correct answer.</instruction>
    <input>key_details</input>
    <output>answer</output>
  </node>
  <end/>
  <edge from="start" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="end"/>