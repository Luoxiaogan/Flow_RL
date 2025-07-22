# Workflow ID: drop_199_0
# Benchmark: drop
# Data Indices: [453, 2403, 1755, 2431, 3299]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify the key numerical data relevant to the question. Extract values and their context from the passage.</instruction>
    <depends_on>1</depends_on>
  </node>
  
  <node id="3" type="agent">
    <instruction>Perform necessary calculations based on extracted values. For example, compute differences, totals, or ratios as required by the question.</instruction>
    <depends_on>2</depends_on>
  </node>
  
  <node id="4" type="agent">
    <instruction>Verify that the computed result aligns with the question's requirement—ensure units, comparisons, and logic are correct.</instruction>
    <depends_on>3</depends_on>
  </node>
  
  <node id="5" type="output">
    <description>Return the final answer as a single numeric value or clearly defined result.</description>
    <depends_on>4</depends_on>
  </node>