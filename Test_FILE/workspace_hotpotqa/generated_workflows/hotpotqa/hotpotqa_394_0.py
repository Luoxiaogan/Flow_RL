# Workflow ID: hotpotqa_394_0
# Benchmark: hotpotqa
# Data Indices: [1910, 1166, 3928, 910]

<operator id="1" type="extract">
        <input>problem</input>
        <output>question, context</output>
        <instruction>Extract the main question and relevant context from the input problem.</instruction>
    </operator>
    
    <operator id="2" type="analyze">
        <input>context</input>
        <output>key_entities</output>
        <instruction>Identify key entities (e.g., names, terms, dates) in the context that relate to the question.</instruction>
    </operator>
    
    <operator id="3" type="match">
        <input>question, key_entities</input>
        <output>candidate_answers</output>
        <instruction>Match the question with the most relevant entities to generate candidate answers.</instruction>
    </operator>
    
    <operator id="4" type="validate">
        <input>candidate_answers</input>
        <output>validated_answer</output>
        <instruction>Validate each candidate answer against the context to ensure accuracy and relevance.</instruction>
    </operator>
    
    <operator id="5" type="ensemble">
        <input>validated_answer</input>
        <output>final_answer</output>
        <instruction>Ensure the validated answer is correct and ready for final output. If multiple valid candidates exist, choose the best one based on contextual support.</instruction>
    </operator>
    
    <operator id="6" type="format">
        <input>final_answer</input>
        <output>formatted_output</output>
        <instruction>Format the final answer clearly and concisely for the user.</instruction>
    </operator>