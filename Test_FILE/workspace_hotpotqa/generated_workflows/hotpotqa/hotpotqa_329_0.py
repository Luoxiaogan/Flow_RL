# Workflow ID: hotpotqa_329_0
# Benchmark: hotpotqa
# Data Indices: [3989, 2292, 186, 1147, 3527]

<node id="1" type="input">
    <prompt>Understand the question and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the cathedral mentioned in the context that had organs restored by Dirk Andries Flentrop in 1977.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Find the construction period of that cathedral from the context.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the years between which the cathedral was built in sections.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>