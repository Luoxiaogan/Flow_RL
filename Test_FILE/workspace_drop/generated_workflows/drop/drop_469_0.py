# Workflow ID: drop_469_0
# Benchmark: drop
# Data Indices: [2164, 1093, 2473, 2869]

<node id="1">
    <operator>extract_relevant_data</operator>
    <input>problem</input>
    <output>filtered_data</output>
  </node>
  <node id="2">
    <operator>identify_question_type</operator>
    <input>filtered_data</input>
    <output>question_category</output>
  </node>
  <node id="3">
    <operator>locate_numerical_values</operator>
    <input>filtered_data</input>
    <output>numerical_info</output>
  </node>
  <node id="4">
    <operator>apply_arithmetic_operation</operator>
    <input>numerical_info</input>
    <output>result</output>
  </node>
  <node id="5">
    <operator>validate_solution</operator>
    <input>result</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>