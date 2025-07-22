# Workflow ID: drop_89_0
# Benchmark: drop
# Data Indices: [2399, 1931, 2502, 2522]

<node id="1">
    <input>problem</input>
    <output>extracted_data</output>
    <agent>Extract relevant player statistics from passage</agent>
    <instruction>Identify all instances where the player of interest (e.g., Neil Rackers, Jay Feely, etc.) is mentioned in relation to field goals or touchdowns. Record each instance with its yardage and quarter.</instruction>
  </node>
  
  <node id="2">
    <input>extracted_data</input>
    <output>filtered_by_player</output>
    <agent>Filter data for specific player</agent>
    <instruction>From the extracted data, isolate only entries that pertain to the player named in the question. Ensure no other players' actions are included.</instruction>
  </node>
  
  <node id="3">
    <input>filtered_by_player</input>
    <output>count_and_summarize</output>
    <agent>Count field goals and sum touchdown pass yards</agent>
    <instruction>For field goal questions: count how many times the player made a field goal. For passing questions: sum the yards of all touchdown passes made by the player.</instruction>
  </node>
  
  <node id="4">
    <input>count_and_summarize</input>
    <output>final_answer</output>
    <agent>Generate final answer based on counts or sums</agent>
    <instruction>Determine whether the question asks for a count (like field goals) or a sum (like touchdown pass yards). Return the appropriate value as an integer.</instruction>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>