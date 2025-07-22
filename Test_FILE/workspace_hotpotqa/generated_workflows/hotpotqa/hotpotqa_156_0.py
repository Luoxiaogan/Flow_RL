# Workflow ID: hotpotqa_156_0
# Benchmark: hotpotqa
# Data Indices: [2974, 3152, 292, 283]

<node id="1">
    <operator>input</operator>
    <output>problem</output>
  </node>
  <node id="2">
    <operator>extract_question</operator>
    <input>problem</input>
    <output>question</output>
  </node>
  <node id="3">
    <operator>extract_context</operator>
    <input>problem</input>
    <output>context</output>
  </node>
  <node id="4">
    <operator>identify_key_entities</operator>
    <input>question</input>
    <output>entities</output>
  </node>
  <node id="5">
    <operator>match_entities_to_context</operator>
    <input>entities, context</input>
    <output>relevant_passages</output>
  </node>
  <node id="6">
    <operator>reason_step_by_step</operator>
    <input>relevant_passages</input>
    <output>reasoning_chain</output>
  </node>
  <node id="7">
    <operator>generate_answer</operator>
    <input>reasoning_chain</input>
    <output>answer</output>
  </node>
  <node id="8">
    <operator>validate_answer</operator>
    <input>answer, context</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="5"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>
  <edge from="6" to="7"/>
  <edge from="7" to="8"/>