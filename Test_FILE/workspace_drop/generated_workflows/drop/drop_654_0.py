# Workflow ID: drop_654_0
# Benchmark: drop
# Data Indices: [175, 3443, 3463, 1380, 126]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the relevant numerical data from the passage that answers the question. Focus on identifying the key values mentioned in the context of the question.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform the necessary arithmetic or logical operation to compute the final answer based on the extracted data. Ensure the operation aligns with the question's requirement (e.g., subtraction, comparison).</instruction>
    <input>extracted_data</input>
    <output>computed_answer</output>
  </node>
  <node id="4" type="output">
    <parameter>computed_answer</parameter>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>