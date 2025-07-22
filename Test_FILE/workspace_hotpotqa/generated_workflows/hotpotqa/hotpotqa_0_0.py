# Workflow ID: hotpotqa_0_0
# Benchmark: hotpotqa
# Data Indices: [2179, 1980, 2698, 3134]

<operator id="1" type="extract">
    <input>problem</input>
    <output>extracted_question, extracted_context</output>
    <instruction>Identify the core question and relevant context from the input problem.</instruction>
  </operator>

  <operator id="2" type="reason">
    <input>extracted_question, extracted_context</input>
    <output>step_by_step_reasoning</output>
    <instruction>Break down the question logically. Use only the extracted context to reason step-by-step toward the answer.</instruction>
  </operator>

  <operator id="3" type="validate">
    <input>step_by_step_reasoning</input>
    <output>validated_answer</output>
    <instruction>Verify that each reasoning step is correct and directly supports the final answer. Eliminate any unsupported assumptions.</instruction>
  </operator>

  <operator id="4" type="format">
    <input>validated_answer</input>
    <output>final_output</output>
    <instruction>Present the answer clearly and concisely in a format suitable for direct use.</instruction>
  </operator>

  <connect from="1" to="2"/>
  <connect from="2" to="3"/>
  <connect from="3" to="4"/>