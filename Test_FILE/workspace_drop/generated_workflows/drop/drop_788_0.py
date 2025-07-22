# Workflow ID: drop_788_0
# Benchmark: drop
# Data Indices: [991, 3478, 2384, 3309, 3006]

<operator id="0" type="extract">
    <input>problem</input>
    <output>extracted_info</output>
    <instruction>Extract the key numerical and categorical data from the input problem.</instruction>
  </operator>
  
  <operator id="1" type="process">
    <input>extracted_info</input>
    <output>processed_data</output>
    <instruction>Process the extracted information to identify relevant values for answering the question. Focus on relationships between entities such as people, teams, years, or quantities.</instruction>
  </operator>
  
  <operator id="2" type="reason">
    <input>processed_data</input>
    <output>reasoned_answer</output>
    <instruction>Reason step-by-step: Identify what is being asked, locate the relevant facts, and compute the answer logically. Avoid assumptions not supported by the passage.</instruction>
  </operator>
  
  <operator id="3" type="validate">
    <input>reasoned_answer</input>
    <output>final_answer</output>
    <instruction>Verify that the answer matches the question exactly and is derived solely from the provided passage. If any ambiguity exists, return 'Unknown'.</instruction>
  </operator>