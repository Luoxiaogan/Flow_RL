# Workflow ID: hotpotqa_203_0
# Benchmark: hotpotqa
# Data Indices: [1635, 42, 3789, 3111]

<agent id="1">
    <instruction>Identify the key entities in the question and locate their corresponding information in the context.</instruction>
    <input>problem</input>
    <output>entity_mapping</output>
  </agent>
  
  <agent id="2">
    <instruction>Extract the relevant details about the actor from "Junooniyat" and determine their other film roles mentioned in the context.</instruction>
    <input>entity_mapping</input>
    <output>actor_details</output>
  </agent>
  
  <agent id="3">
    <instruction>Find the 2012 movie that features the same actor as in "Junooniyat", based on the extracted details.</instruction>
    <input>actor_details</input>
    <output>movie_result</output>
  </agent>
  
  <agent id="4">
    <instruction>Verify the match by cross-referencing the actor's name and the year of the movie to ensure accuracy.</instruction>
    <input>movie_result</input>
    <output>final_answer</output>
  </agent>