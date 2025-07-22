# Workflow ID: drop_598_0
# Benchmark: drop
# Data Indices: [3735, 343, 3186, 2003]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data points in the passage relevant to the question. Extract values, ranges, or percentages that directly answer the query.</instruction>
    <input>1</input>
    <output>key_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Apply logical reasoning to determine how the extracted data answers the specific question. If multiple values are present, select the one(s) that match the criteria (e.g., range, condition).</instruction>
    <input>2</input>
    <output>answer_candidate</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the answer candidate aligns with the question's requirements and matches the format expected (e.g., integer, percentage, list). If ambiguous, resolve based on context from the passage.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="output">
    <param>final_answer</param>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>