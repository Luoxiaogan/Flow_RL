# Workflow ID: hotpotqa_520_0
# Benchmark: hotpotqa
# Data Indices: [1690, 2801, 1269, 2366]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the singer who wrote "What the Water Gave Me".</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Determine the birth year of that singer.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <prompt>Return the birth year of the singer who wrote "What the Water Gave Me".</prompt>
    <depends_on>3</depends_on>
  </node>