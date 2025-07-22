# Workflow ID: hotpotqa_342_0
# Benchmark: hotpotqa
# Data Indices: [2297, 590, 3783, 1158, 3574]

<node id="1" type="question_analysis">
        <input>problem</input>
        <output>analyzed_question</output>
        <instruction>Break down the question to identify key entities and relationships. Focus on what is being asked and what information is needed.</instruction>
    </node>
    
    <node id="2" type="context_retrieval">
        <input>analyzed_question</input>
        <output>relevant_context</output>
        <instruction>Extract only the context that directly relates to the key entities in the question. Ignore unrelated details.</instruction>
    </node>
    
    <node id="3" type="entity_resolution">
        <input>relevant_context</input>
        <output>resolved_entities</output>
        <instruction>Identify and clarify the exact entities mentioned (e.g., people, organizations, events). Resolve ambiguities if present.</instruction>
    </node>
    
    <node id="4" type="relationship_mapping">
        <input>resolved_entities</input>
        <output>relationships</output>
        <instruction>Map how the entities are connected based on the context—e.g., "X worked with Y", "Z was founded by A".</instruction>
    </node>
    
    <node id="5" type="answer_generation">
        <input>relationships</input>
        <output>final_answer</output>
        <instruction>Construct a clear and concise answer based on the mapped relationships. Ensure it directly answers the original question.</instruction>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>