# Workflow ID: drop_276_0
# Benchmark: drop
# Data Indices: [2493, 2898, 2107, 2920]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations or comparisons based on the extracted data to derive the answer.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the result by cross-checking with the original passage for accuracy.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <data>final_answer</data>
    <depends_on>4</depends_on>
  </node>