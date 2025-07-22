# Workflow ID: hotpotqa_124_0
# Benchmark: hotpotqa
# Data Indices: [3223, 2377, 2199, 644, 3080]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem statement. Break down the question into its core components.</instruction>
        <input>problem</input>
        <output>structured_entities</output>
    </operator>
    
    <operator id="2">
        <instruction>Map each entity to known data points from the context provided. Focus on direct matches or logical connections.</instruction>
        <input>structured_entities, context</input>
        <output>candidate_answers</output>
    </operator>
    
    <operator id="3">
        <instruction>Filter candidates based on relevance, specificity, and alignment with the question's focus (e.g., name, event, date).</instruction>
        <input>candidate_answers</input>
        <output>filtered_candidates</output>
    </operator>
    
    <operator id="4">
        <instruction>Validate the top candidate(s) by cross-referencing with contextual clues that support or refute them.</instruction>
        <input>filtered_candidates, context</input>
        <output>validated_answer</output>
    </operator>
    
    <operator id="5">
        <instruction>Ensure the final answer is unambiguous and directly addresses the original question without extraneous details.</instruction>
        <input>validated_answer</input>
        <output>final_answer</output>
    </operator>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>