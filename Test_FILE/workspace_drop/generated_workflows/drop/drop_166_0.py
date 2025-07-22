# Workflow ID: drop_166_0
# Benchmark: drop
# Data Indices: [2542, 3552, 396, 3554, 3295]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage. Identify all yardage values mentioned in relation to touchdowns and field goals.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific touchdown mentioned in the question: Packers' first touchdown.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Identify the Lions' touchdown mentioned in the question: their only score in the first half.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="5" type="agent">
    <instruction>Calculate the difference between the Packers' first touchdown and the Lions' touchdown.</instruction>
    <depends_on>3,4</depends_on>
  </node>
  <node id="6" type="output">
    <instruction>Return the calculated difference in yards.</instruction>
    <depends_on>5</depends_on>
  </node>