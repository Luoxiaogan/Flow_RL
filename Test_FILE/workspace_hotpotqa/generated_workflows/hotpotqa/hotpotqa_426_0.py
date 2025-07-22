# Workflow ID: hotpotqa_426_0
# Benchmark: hotpotqa
# Data Indices: [2308, 1472, 382, 1110, 177]

<node id="1" type="agent">
    <instruction>Identify the key entities and relationships in the problem. Break down the question into its core components to determine what information is needed to solve it.</instruction>
  </node>
  <node id="2" type="agent">
    <instruction>Search for relevant context that directly answers the question. Focus on specific details like names, events, or outcomes mentioned in the problem.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Verify the accuracy of the candidate answer by cross-referencing with multiple sources in the context to ensure consistency and correctness.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Generate a final response based on the verified information, ensuring clarity and precision in answering the original question.</instruction>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>