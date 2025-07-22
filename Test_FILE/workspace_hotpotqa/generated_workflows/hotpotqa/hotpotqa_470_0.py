# Workflow ID: hotpotqa_470_0
# Benchmark: hotpotqa
# Data Indices: [3140, 1279, 1422, 3730, 2455]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the release year of 'Beauty and the Beast' (2017 film).</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Identify the release year of 'Davy Crockett, King of the Wild Frontier' (1955 film).</prompt>
  </node>
  <node id="4" type="operator">
    <prompt>Compare the two years to determine which movie was released first.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the movie that was released first based on the comparison.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>