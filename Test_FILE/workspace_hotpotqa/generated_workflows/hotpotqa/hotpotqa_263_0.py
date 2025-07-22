# Workflow ID: hotpotqa_263_0
# Benchmark: hotpotqa
# Data Indices: [3745, 261, 1048, 2066, 1307]

<operator id="1">
    <instruction>Identify the actor who played Tracy Billings in "The Hangover Trilogy".</instruction>
    <input>problem</input>
    <output>actor_name</output>
  </operator>
  
  <operator id="2">
    <instruction>Determine the acting instructor of the identified actor.</instruction>
    <input>actor_name</input>
    <output>instructor_name</output>
  </operator>
  
  <operator id="3">
    <instruction>Verify that the acting instructor is a known professional with documented teaching experience.</instruction>
    <input>instructor_name</input>
    <output>valid_instructor</output>
  </operator>
  
  <operator id="4">
    <instruction>Return the final answer: the name of the acting instructor.</instruction>
    <input>valid_instructor</input>
    <output>final_answer</output>
  </operator>