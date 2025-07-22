# Workflow ID: hotpotqa_106_0
# Benchmark: hotpotqa
# Data Indices: [3415, 3811, 2154, 3909]

<node id="1" type="input">
    <prompt>Understand the core question and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the country based on the location of Cabañeros National Park.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Identify the country based on the location of Tablas de Daimiel National Park.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that both parks are in the same country by cross-checking geographic data.</prompt>
    <depends_on>2,3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the common country where both national parks are located.</prompt>
    <depends_on>4</depends_on>
  </node>