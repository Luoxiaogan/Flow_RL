# Workflow ID: drop_733_0
# Benchmark: drop
# Data Indices: [3382, 3673, 1974, 3926]

<node id="1">
    <input>problem</input>
    <output>extract_question_and_passage</output>
    <operator>extract_question_and_passage</operator>
  </node>
  <node id="2">
    <input>extract_question_and_passage</input>
    <output>parse_question</output>
    <operator>parse_question</operator>
  </node>
  <node id="3">
    <input>extract_question_and_passage</input>
    <output>identify_key_entities</output>
    <operator>identify_key_entities</operator>
  </node>
  <node id="4">
    <input>parse_question</input>
    <output>determine_comparison_type</output>
    <operator>determine_comparison_type</operator>
  </node>
  <node id="5">
    <input>identify_key_entities</input>
    <output>locate_values_in_passage</output>
    <operator>locate_values_in_passage</operator>
  </node>
  <node id="6">
    <input>determine_comparison_type</input>
    <input>locate_values_in_passage</input>
    <output>compare_values</output>
    <operator>compare_values</operator>
  </node>
  <node id="7">
    <input>compare_values</input>
    <output>generate_final_answer</output>
    <operator>generate_final_answer</operator>
  </node>
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="5"/>
  <edge from="4" to="6"/>
  <edge from="5" to="6"/>
  <edge from="6" to="7"/>