# Workflow ID: hotpotqa_516_0
# Benchmark: hotpotqa
# Data Indices: [1549, 1893, 2878, 813]

<node id="1" type="input">
    <prompt>Understand the core question and identify key entities involved.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant dates or time-based information from the context for each project mentioned.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted dates to determine which project was completed earlier.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the name of the older project based on the comparison.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>