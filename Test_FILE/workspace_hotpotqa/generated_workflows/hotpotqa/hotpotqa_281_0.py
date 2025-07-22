# Workflow ID: hotpotqa_281_0
# Benchmark: hotpotqa
# Data Indices: [2023, 2778, 2691, 2171]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem context. Focus on extracting explicit facts and connections between named entities.</instruction>
        <input>problem</input>
        <output>entity_relations</output>
    </operator>
    
    <operator id="1">
        <instruction>For each entity, determine if it has a known location or origin. If so, map it to its geographical or organizational base.</instruction>
        <input>entity_relations</input>
        <output>location_mapping</output>
    </operator>
    
    <operator id="2">
        <instruction>Filter only the relevant entity that matches the question's subject (e.g., 'band Frank Benbini is a member of'). Extract its location from the mapping.</instruction>
        <input>location_mapping</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="3">
        <instruction>Validate the final answer by cross-checking with the original context for any conflicting information or missing links.</instruction>
        <input>final_answer, problem</input>
        <output>validated_answer</output>
    </operator>
    
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>