# Workflow ID: hotpotqa_95_0
# Benchmark: hotpotqa
# Data Indices: [2755, 3474, 2812, 2416]

<operator id="1" type="agent">
    <instruction>Identify the key entities in the question and context that relate to the opera by Hugo von Hofmannsthal featuring Aatos Abel Tapala.</instruction>
    <input>problem</input>
    <output>entity_matches</output>
  </operator>
  
  <operator id="2" type="agent">
    <instruction>From the matches, determine which opera by Hugo von Hofmannsthal includes Aatos Abel Tapala as a performer.</instruction>
    <input>entity_matches</input>
    <output>opera_candidate</output>
  </operator>
  
  <operator id="3" type="agent">
    <instruction>Verify if the candidate opera is indeed based on a libretto by Hugo von Hofmannsthal and if Aatos Abel Tapala performed in it.</instruction>
    <input>opera_candidate</input>
    <output>verification_result</output>
  </operator>
  
  <operator id="4" type="agent">
    <instruction>If verified, return the name of the opera; otherwise, indicate no valid match was found.</instruction>
    <input>verification_result</input>
    <output>final_answer</output>
  </operator>