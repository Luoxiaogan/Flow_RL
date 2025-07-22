# Workflow ID: drop_191_0
# Benchmark: drop
# Data Indices: [1234, 388, 2992, 2840, 3380]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that relates to the question. Identify key figures such as yardages, counts, or percentages mentioned in the context of the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify which numbers directly answer the question. For example, if the question asks for a difference, locate the two values involved in the subtraction. If it's about totals, sum up the relevant quantities.</instruction>
    <input>2</input>
    <output>identified_values</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform the required mathematical operation (e.g., subtraction, addition, comparison) using the identified values. Ensure the calculation is accurate and matches the question's intent.</instruction>
    <input>3</input>
    <output>calculated_result</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify that the calculated result logically answers the original question. Double-check units, context, and whether all relevant data has been considered.</instruction>
    <input>4</input>
    <output>final_answer</output>
  </node>
  <node id="6" type="output">
    <param>final_answer</param>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>