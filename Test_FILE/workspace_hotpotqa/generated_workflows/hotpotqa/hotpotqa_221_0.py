# Workflow ID: hotpotqa_221_0
# Benchmark: hotpotqa
# Data Indices: [1292, 2241, 258, 1733]

<agent id="1" type="reasoning">
    <instruction>Think step by step to identify the key relationship between Karl von Eberstein and the Sturmabteilung (SA).</instruction>
    <input>context</input>
    <output>agent_2_input</output>
  </agent>
  
  <agent id="2" type="retrieval">
    <instruction>Extract specific details about Karl von Eberstein's affiliations with Nazi organizations from the context.</instruction>
    <input>agent_1_output</input>
    <output>agent_3_input</output>
  </agent>
  
  <agent id="3" type="synthesis">
    <instruction>Combine the extracted information to clearly state how Karl von Eberstein is related to the Sturmabteilung.</instruction>
    <input>agent_2_output</input>
    <output>final_answer</output>
  </agent>