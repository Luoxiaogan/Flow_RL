# Workflow ID: hotpotqa_72_0
# Benchmark: hotpotqa
# Data Indices: [1071, 494, 887, 3819]

<node id="1" type="question_analysis">
    <input>problem</input>
    <output>extracted_question, extracted_context</output>
    <instruction>Identify the core question and relevant context from the input problem.</instruction>
  </node>

  <node id="2" type="context_filtering">
    <input>extracted_context</input>
    <output>filtered_context</output>
    <instruction>Extract only the sentences directly related to the question's subject matter.</instruction>
  </node>

  <node id="3" type="entity_resolution">
    <input>filtered_context</input>
    <output>key_entities</output>
    <instruction>Identify key entities (names, dates, places) that are central to answering the question.</instruction>
  </node>

  <node id="4" type="fact_extraction">
    <input>key_entities</input>
    <output>facts</output>
    <instruction>From the filtered context, extract precise facts that answer the question.</instruction>
  </node>

  <node id="5" type="answer_validation">
    <input>facts</input>
    <output>validated_answer</output>
    <instruction>Verify the extracted fact is unambiguous, directly answers the question, and matches the expected format.</instruction>
  </node>

  <node id="6" type="final_output">
    <input>validated_answer</input>
    <output>answer</output>
    <instruction>Return the final correct answer in plain text.</instruction>
  </node>

  <!-- Edges -->
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>