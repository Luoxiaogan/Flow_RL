# Workflow ID: drop_233_0
# Benchmark: drop
# Data Indices: [1718, 2353, 200, 2777]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key elements in the passage related to the question. Focus on specific events, dates, or numerical values mentioned.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract relevant data points that answer the question. If multiple pieces of information are present, determine which ones are directly applicable.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Compare or calculate based on the extracted data. For example, if comparing two dates, determine which occurred first; if counting, tally only those that meet the condition.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the final result by cross-checking against the passage to ensure accuracy and completeness.</instruction>
    <input>4</input>
    <output>5</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>