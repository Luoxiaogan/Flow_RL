# Workflow ID: drop_42_0
# Benchmark: drop
# Data Indices: [2229, 769, 3694, 1378]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key entities and relationships in the problem statement. Break down the question to determine what information is needed to answer it.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract relevant data from the passage that directly relates to the question. Focus only on the specific details required to answer the query, avoiding irrelevant context.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Process the extracted data to derive a precise answer. If multiple pieces of information are present, determine how they interact to form the final response.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the answer by cross-checking with the original passage to ensure accuracy and completeness.</instruction>
    <input>4</input>
    <output>5</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>