# Workflow ID: hotpotqa_275_0
# Benchmark: hotpotqa
# Data Indices: [2557, 1300, 2884, 769, 1122]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem statement. Focus on extracting the main subject, the award, the year, and the film title.</instruction>
        <input>problem</input>
        <output>extracted_info</output>
    </operator>
    
    <operator id="2">
        <instruction>Determine the lead actor or actress in the film that won the Silver Bear at the Berlin International Film Festival in 2016.</instruction>
        <input>extracted_info</input>
        <output>film_title</output>
    </operator>
    
    <operator id="3">
        <instruction>Using the film title from step 2, locate the primary cast member (actor/actress) who starred in that film.</instruction>
        <input>film_title</input>
        <output>lead_actor_or_actress</output>
    </operator>
    
    <operator id="4">
        <instruction>Verify that the lead actor or actress identified in step 3 matches the winner of the Silver Bear for Best Actress or Best Actor at the 2016 Berlin Film Festival.</instruction>
        <input>lead_actor_or_actress</input>
        <output>final_answer</output>
    </operator>