# Workflow ID: drop_162_0
# Benchmark: drop
# Data Indices: [2303, 848, 2065, 3210, 2143]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract key information from the passage relevant to the question. Identify numerical values, categories, or direct answers.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Process the extracted data to determine the correct answer by comparing or calculating based on the context provided.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the solution by cross-checking with the original passage to ensure accuracy and relevance.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>