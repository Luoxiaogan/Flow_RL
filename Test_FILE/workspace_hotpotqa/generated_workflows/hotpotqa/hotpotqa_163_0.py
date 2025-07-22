# Workflow ID: hotpotqa_163_0
# Benchmark: hotpotqa
# Data Indices: [1207, 3513, 753, 2270]

<agent id="1" type="reasoning">
    <instruction>Think step by step to identify the key elements in the question and context that relate to the full name of the man who inspired "Stand by Me". Focus on connections between the song, its writers, and any references to real-life inspirations.</instruction>
    <input>problem</input>
    <output>inspiration_clue</output>
  </agent>
  
  <agent id="2" type="search">
    <instruction>Based on the clue from Agent 1, search for historical or biographical information about Ben E. King, Sam Cooke, and the origin of the song "Stand by Me". Identify if either artist was directly inspired by someone else.</instruction>
    <input>inspiration_clue</input>
    <output>potential_inspiration</output>
  </agent>
  
  <agent id="3" type="verification">
    <instruction>Verify whether the potential inspiration identified by Agent 2 is explicitly mentioned as the source of inspiration for "Stand by Me". Cross-reference with reliable sources such as interviews, liner notes, or official biographies.</instruction>
    <input>potential_inspiration</input>
    <output>verified_inspiration</output>
  </agent>
  
  <agent id="4" type="synthesis">
    <instruction>Combine the verified inspiration from Agent 3 with the known facts about the song's creation. If a specific individual is confirmed as the inspiration, provide their full name as the final answer.</instruction>
    <input>verified_inspiration</input>
    <output>final_answer</output>
  </agent>
  
  <connect from="1" to="2"/>
  <connect from="2" to="3"/>
  <connect from="3" to="4"/>