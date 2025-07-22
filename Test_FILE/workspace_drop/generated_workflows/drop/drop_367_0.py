# Workflow ID: drop_367_0
# Benchmark: drop
# Data Indices: [3001, 748, 1390, 351]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data relevant to the question. Extract all yardage values mentioned in the passage related to the subject of the question.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Compare or calculate based on the extracted values. If the question asks for a difference, subtract the smaller value from the larger one. If it's about finding a maximum or minimum, determine accordingly.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the calculated result matches the exact wording and intent of the question. Ensure no misinterpretation of units or context (e.g., field goal vs. touchdown).</instruction>
  </node>
  <node id="5" type="output">
    <description>Return the final numerical answer as an integer</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>