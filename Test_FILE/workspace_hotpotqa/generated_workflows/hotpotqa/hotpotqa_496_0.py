# Workflow ID: hotpotqa_496_0
# Benchmark: hotpotqa
# Data Indices: [3526, 3898, 802, 2966]

<operator id="1" type="agent">
    <instruction>Identify the key elements in the question: the film title, director, and the need to find the soundtrack label.</instruction>
    <input>problem</input>
    <output>film_info</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Extract from context the relevant information about the film directed by John Curran in 2006.</instruction>
    <input>film_info</input>
    <output>film_details</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>From the extracted film details, locate the soundtrack information and its label.</instruction>
    <input>film_details</input>
    <output>soundtrack_label</output>
  </operator>
  <operator id="4" type="agent">
    <instruction>Verify that the label found matches the release of the soundtrack for John Curran's 2006 drama film.</instruction>
    <input>soundtrack_label</input>
    <output>verified_label</output>
  </operator>
  <operator id="5" type="agent">
    <instruction>Return the verified label as the final answer.</instruction>
    <input>verified_label</input>
    <output>final_answer</output>
  </operator>