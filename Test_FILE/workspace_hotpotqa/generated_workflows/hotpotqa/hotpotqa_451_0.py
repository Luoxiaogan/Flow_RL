# Workflow ID: hotpotqa_451_0
# Benchmark: hotpotqa
# Data Indices: [817, 2608, 894, 1898]

<node id="1" type="input">
    <prompt>Understand the core question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant facts from context for each entity mentioned in the question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted facts to determine the answer based on the question's criteria.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <prompt>Return the final answer derived from the comparison.</prompt>
    <depends_on>3</depends_on>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>