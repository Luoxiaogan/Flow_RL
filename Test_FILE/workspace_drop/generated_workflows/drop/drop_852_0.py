# Workflow ID: drop_852_0
# Benchmark: drop
# Data Indices: [2667, 871, 504, 3206, 403]

<node id="1">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <output>numerical_data</output>
  </node>
  <node id="2">
    <instruction>Identify the key values needed to solve the problem based on the question's context.</instruction>
    <output>key_values</output>
  </node>
  <node id="3">
    <instruction>Apply mathematical operations (e.g., subtraction, percentage calculation) to derive the answer using key values.</instruction>
    <output>intermediate_result</output>
  </node>
  <node id="4">
    <instruction>Validate the intermediate result against the passage to ensure accuracy and logical consistency.</instruction>
    <output>validated_result</output>
  </node>
  <node id="5">
    <instruction>Format the final answer in a clear and concise way that directly addresses the question.</instruction>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>