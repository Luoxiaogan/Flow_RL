# Workflow ID: hotpotqa_343_0
# Benchmark: hotpotqa
# Data Indices: [2685, 1993, 1983, 2921]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context about the band in question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Find the debut album release year for Godspeed You! Black Emperor.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Find the debut album release year for Halestorm.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="5" type="agent">
    <prompt>Compare the two years to determine which band released their debut more recently.</prompt>
    <depends_on>3,4</depends_on>
  </node>
  <node id="6" type="output">
    <prompt>Return the name of the band that released their debut album more recently.</prompt>
    <depends_on>5</depends_on>
  </node>