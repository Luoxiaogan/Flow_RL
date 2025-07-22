# Workflow ID: hotpotqa_39_0
# Benchmark: hotpotqa
# Data Indices: [93, 1606, 3634, 2613]

<start/>
  <agent id="1" type="reasoning">
    <instruction>Identify the key elements in the question and context to determine the correct answer.</instruction>
    <input>problem</input>
    <output>step_1_output</output>
  </agent>
  <agent id="2" type="filter">
    <instruction>Extract relevant information from the context that directly answers the question.</instruction>
    <input>step_1_output</input>
    <output>step_2_output</output>
  </agent>
  <agent id="3" type="compare">
    <instruction>Compare the extracted information with the possible answers to find the match.</instruction>
    <input>step_2_output</input>
    <output>step_3_output</output>
  </agent>
  <agent id="4" type="validate">
    <instruction>Verify the correctness of the answer by cross-referencing with known facts or additional context.</instruction>
    <input>step_3_output</input>
    <output>final_answer</output>
  </agent>
  <end/>