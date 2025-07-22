# Workflow ID: hotpotqa_114_0
# Benchmark: hotpotqa
# Data Indices: [2203, 3186, 2309, 716]

<node id="1">
    <operator>extract_relevant_info</operator>
    <input>problem</input>
    <output>filtered_context</output>
  </node>
  <node id="2">
    <operator>identify_key_entities</operator>
    <input>filtered_context</input>
    <output>key_entities</output>
  </node>
  <node id="3">
    <operator>map_entities_to_questions</operator>
    <input>key_entities</input>
    <output>question_mapping</output>
  </node>
  <node id="4">
    <operator>validate_answers</operator>
    <input>question_mapping</input>
    <output>validated_answers</output>
  </node>
  <node id="5">
    <operator>assemble_final_output</operator>
    <input>validated_answers</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>