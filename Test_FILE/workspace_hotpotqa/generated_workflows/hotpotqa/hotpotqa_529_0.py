# Workflow ID: hotpotqa_529_0
# Benchmark: hotpotqa
# Data Indices: [2828, 2560, 3566, 3209, 2244]

<agent id="1" type="reasoning">
    <instruction>Think step by step to identify the key events and timeline related to the Treaty of Roskilde.</instruction>
    <input>problem</input>
    <output>timeline_analysis</output>
  </agent>
  
  <agent id="2" type="retrieval">
    <instruction>Extract specific dates and military campaigns directly linked to the Treaty of Roskilde from the context.</instruction>
    <input>timeline_analysis</input>
    <output>campaign_dates</output>
  </agent>
  
  <agent id="3" type="validation">
    <instruction>Verify that the extracted dates align with historical records of the Second Northern War and the campaign leading to the treaty.</instruction>
    <input>campaign_dates</input>
    <output>validated_dates</output>
  </agent>
  
  <agent id="4" type="synthesis">
    <instruction>Combine validated dates into a coherent chronological sequence showing the campaign path to the Treaty of Roskilde.</instruction>
    <input>validated_dates</input>
    <output>final_timeline</output>
  </agent>
  
  <agent id="5" type="formatting">
    <instruction>Format the final timeline as a list of key dates in order, suitable for direct output.</instruction>
    <input>final_timeline</input>
    <output>formatted_output</output>
  </agent>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>