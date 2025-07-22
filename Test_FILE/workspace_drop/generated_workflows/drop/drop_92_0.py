# Workflow ID: drop_92_0
# Benchmark: drop
# Data Indices: [3488, 1197, 2109, 352, 3289]

<node id="1" type="input">
    <prompt>Understand the question and identify key numerical data needed.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant values from the passage that relate to the question. Focus on percentages, distances, or counts as required.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary calculations: e.g., subtraction for percentages, differences for yardages, or counting promotions based on text.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the calculated result aligns with the question's requirements—e.g., ensure percentage is of non-Asian population, not Asian.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer in the format specified by the problem (e.g., number, percentage, or yard difference).</prompt>
    <depends_on>4</depends_on>
  </node>