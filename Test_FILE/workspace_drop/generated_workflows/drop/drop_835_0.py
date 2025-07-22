# Workflow ID: drop_835_0
# Benchmark: drop
# Data Indices: [1677, 964, 2855, 3017]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Extract key numerical data from the passage relevant to the question. Think step by step: identify the entities mentioned, locate numbers tied to those entities, and determine which number answers the question.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Verify that the extracted number is directly answering the question. If not, re-examine the passage for any missing or misinterpreted data. Ensure no arithmetic operation is needed unless explicitly required by the question.</instruction>
  </node>
  <node id="4" type="output">
    <description>Return the final answer as an integer or float, depending on the problem's nature.</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>