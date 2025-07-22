# Workflow ID: hotpotqa_338_0
# Benchmark: hotpotqa
# Data Indices: [3118, 1837, 3733, 933]

<operator id="1" type="agent">
    <instruction>Identify the key elements in the problem statement that relate to historical programs and their timeframes.</instruction>
    <input>problem</input>
    <output>key_elements</output>
  </operator>
  
  <operator id="2" type="agent">
    <instruction>Match the key elements to known public work relief programs active between 1933 and 1942, particularly those focused on unemployed, unmarried men from relief families.</instruction>
    <input>key_elements</input>
    <output>potential_programs</output>
  </operator>
  
  <operator id="3" type="agent">
    <instruction>Verify which of these programs is directly associated with the construction of rustic cottages in state parks like Monte Sano.</instruction>
    <input>potential_programs</input>
    <output>verified_program</output>
  </operator>
  
  <operator id="4" type="agent">
    <instruction>Confirm the timeframe and purpose of the verified program to ensure it aligns with the era described in the problem (1933–1942 for unemployed, unmarried men).</instruction>
    <input>verified_program</input>
    <output>final_verification</output>
  </operator>
  
  <operator id="5" type="agent">
    <instruction>Return the name of the public work relief program based on the final verification.</instruction>
    <input>final_verification</input>
    <output>answer</output>
  </operator>