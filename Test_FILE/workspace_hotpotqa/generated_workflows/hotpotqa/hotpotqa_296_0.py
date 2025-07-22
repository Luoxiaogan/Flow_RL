# Workflow ID: hotpotqa_296_0
# Benchmark: hotpotqa
# Data Indices: [1990, 1394, 2949, 2830]

<agent id="1" type="extraction">
        <instruction>Extract key entities and relationships from the context that are relevant to the question.</instruction>
        <input>problem</input>
        <output>entities_and_relations</output>
    </agent>
    
    <agent id="2" type="filtering">
        <instruction>Filter out irrelevant entities and focus only on those directly related to the question's subject (e.g., military unit, location, airport).</instruction>
        <input>entities_and_relations</input>
        <output>filtered_entities</output>
    </agent>
    
    <agent id="3" type="mapping">
        <instruction>Map the filtered entities to possible answers by aligning them with known patterns or structures (e.g., "stationed at X" implies X is the answer).</instruction>
        <input>filtered_entities</input>
        <output>candidate_answers</output>
    </agent>
    
    <agent id="4" type="validation">
        <instruction>Validate candidate answers against all contextual clues to ensure accuracy—check for consistency in units, locations, and timeframes.</instruction>
        <input>candidate_answers</input>
        <output>validated_answer</output>
    </agent>
    
    <agent id="5" type="ensemble">
        <instruction>Combine the validated answer with any supporting evidence or metadata from previous steps to produce a final, well-supported response.</instruction>
        <input>validated_answer</input>
        <output>final_output</output>
    </agent>