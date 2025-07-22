# Workflow ID: hotpotqa_295_0
# Benchmark: hotpotqa
# Data Indices: [1390, 1605, 476, 3880]

<operator id="1" type="agent">
    <instruction>Think step by step to determine which work has been seen in more than one language.</instruction>
    <input>problem</input>
    <output>analysis_1</output>
  </operator>
  
  <operator id="2" type="agent">
    <instruction>Identify the languages each work has been performed or published in, based on the context provided.</instruction>
    <input>analysis_1</input>
    <output>language_data</output>
  </operator>
  
  <operator id="3" type="agent">
    <instruction>Compare the number of languages for each work and determine which one exceeds one language.</instruction>
    <input>language_data</input>
    <output>comparison_result</output>
  </operator>
  
  <operator id="4" type="agent">
    <instruction>Return the name of the work that has been seen in more than one language.</instruction>
    <input>comparison_result</input>
    <output>final_answer</output>
  </operator>