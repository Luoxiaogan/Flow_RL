# Workflow ID: hotpotqa_272_0
# Benchmark: hotpotqa
# Data Indices: [2135, 2891, 313, 1524]

<node id="1" type="input">
    <description>Receive problem context and question</description>
  </node>
  <node id="2" type="agent">
    <instruction>Identify key entities and relevant facts in the context related to the question.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Extract precise information from the context that directly answers the question, focusing on exact values or names.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the extracted answer is unambiguous and matches the question's requirement (e.g., name, year, formula).</instruction>
  </node>
  <node id="5" type="output">
    <description>Return the final answer as a concise string.</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>