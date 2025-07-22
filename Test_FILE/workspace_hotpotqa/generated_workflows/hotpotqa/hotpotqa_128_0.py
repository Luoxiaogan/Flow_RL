# Workflow ID: hotpotqa_128_0
# Benchmark: hotpotqa
# Data Indices: [3393, 1171, 3855, 372]

<operator id="1" type="agent">
    <instruction>Identify the key entities and relationships in the context to determine the nationality of the concentration camp commandant who was succeeded by Arnold Büscher.</instruction>
    <input>context</input>
    <output>candidate_commandant</output>
  </operator>
  
  <operator id="2" type="agent">
    <instruction>Verify the nationality of the identified commandant by cross-referencing with known historical records or contextual clues about SS officers during WWII.</instruction>
    <input>candidate_commandant</input>
    <output>nationality</output>
  </operator>
  
  <operator id="3" type="agent">
    <instruction>Ensure that the succession from the commandant to Arnold Büscher is correctly mapped, confirming that the identified individual indeed preceded Büscher in command.</instruction>
    <input>candidate_commandant</input>
    <output>valid_succession</output>
  </operator>
  
  <operator id="4" type="agent">
    <instruction>Aggregate the verified nationality and succession validity to produce a final answer.</instruction>
    <input>nationality valid_succession</input>
    <output>final_answer</output>
  </operator>