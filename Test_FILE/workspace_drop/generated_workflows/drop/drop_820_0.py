# Workflow ID: drop_820_0
# Benchmark: drop
# Data Indices: [21, 1700, 405, 1811, 1917]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage related to the question. Focus on specific details like names, numbers, and events that directly answer the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Process the extracted data by filtering out irrelevant information and organizing it into a structured format (e.g., list of values, counts, or sums).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Apply necessary calculations or logical reasoning based on the organized data to derive the final answer.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the computed result as the final answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>