# Workflow ID: drop_611_0
# Benchmark: drop
# Data Indices: [3882, 1178, 2989, 3953]

<node id="1" type="input">
    <prompt>Understand the question and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify which player is mentioned in relation to field goals in the passage.</prompt>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="agent">
    <prompt>Count the number of field goals each player made based on the passage.</prompt>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="operator">
    <prompt>Compare the counts: if Matt Prater's field goals > Rob Bironas's, return "Matt Prater"; else if Rob Bironas's > Matt Prater's, return "Rob Bironas"; otherwise, return "Equal".</prompt>
    <dependencies>3</dependencies>
  </node>
  <node id="5" type="output">
    <prompt>Return the player with more field goals.</prompt>
    <dependencies>4</dependencies>
  </node>