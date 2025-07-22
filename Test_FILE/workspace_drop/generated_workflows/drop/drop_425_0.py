# Workflow ID: drop_425_0
# Benchmark: drop
# Data Indices: [3959, 2088, 674, 1367, 2272]

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
    <output>generate_reasoning_steps</output>
    <operator>generate_reasoning_steps</operator>
  </node>
  <node id="5">
    <input>identify_key_entities</input>
    <output>locate_answer_in_passage</output>
    <operator>locate_answer_in_passage</operator>
  </node>
  <node id="6">
    <input>generate_reasoning_steps</input>
    <output>validate_reasoning</output>
    <operator>validate_reasoning</operator>
  </node>
  <node id="7">
    <input>locate_answer_in_passage</input>
    <output>verify_answer</output>
    <operator>verify_answer</operator>
  </node>
  <node id="8">
    <input>validate_reasoning, verify_answer</input>
    <output>final_answer</output>
    <operator>final_answer</operator>
  </node>