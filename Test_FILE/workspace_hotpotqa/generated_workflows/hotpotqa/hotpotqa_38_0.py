# Workflow ID: hotpotqa_38_0
# Benchmark: hotpotqa
# Data Indices: [2550, 3054, 1737, 62]

<node id="1">
    <operator>extract_question</operator>
    <input>problem</input>
    <output>question</output>
  </node>
  <node id="2">
    <operator>extract_context</operator>
    <input>problem</input>
    <output>context</output>
  </node>
  <node id="3">
    <operator>identify_key_entities</operator>
    <input>context</input>
    <output>entities</output>
  </node>
  <node id="4">
    <operator>map_entities_to_concepts</operator>
    <input>entities</input>
    <output>concepts</output>
  </node>
  <node id="5">
    <operator>reason_step_by_step</operator>
    <input>concepts, question</input>
    <output>answer</output>
  </node>
  <node id="6">
    <operator>validate_answer</operator>
    <input>answer, context</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="5"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>