# Workflow ID: drop_847_0
# Benchmark: drop
# Data Indices: [850, 147, 3701, 3075]

<node id="1">
    <operator>extract_relevant_info</operator>
    <input>problem</input>
    <output>filtered_info</output>
  </node>
  <node id="2">
    <operator>identify_question_type</operator>
    <input>filtered_info</input>
    <output>question_category</output>
  </node>
  <node id="3">
    <operator>locate_answer_in_text</operator>
    <input>filtered_info, question_category</input>
    <output>candidate_answer</output>
  </node>
  <node id="4">
    <operator>validate_answer</operator>
    <input>candidate_answer, filtered_info</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>