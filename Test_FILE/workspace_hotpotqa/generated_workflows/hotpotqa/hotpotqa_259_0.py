# Workflow ID: hotpotqa_259_0
# Benchmark: hotpotqa
# Data Indices: [645, 3157, 3288, 3822, 3374]

<node id="1" type="input">
    <prompt>Understand the core question and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the injured quarterback from the 2004 Chicago Bears season.</prompt>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="agent">
    <prompt>Determine which college this quarterback played for.</prompt>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="output">
    <prompt>Return the college name where the injured quarterback played football.</prompt>
    <dependencies>3</dependencies>
  </node>