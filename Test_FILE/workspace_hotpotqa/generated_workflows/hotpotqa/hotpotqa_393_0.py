# Workflow ID: hotpotqa_393_0
# Benchmark: hotpotqa
# Data Indices: [2411, 2784, 194, 440, 3464]

<node id="1" type="input">
        <description>Receive problem context and question</description>
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify key entities mentioned in the context relevant to the question. Focus on names, titles, or descriptors that may link to a specific country.</instruction>
        <input>1</input>
        <output>entity_list</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>For each entity, determine its origin by cross-referencing known geographic associations (e.g., bands, artists, or groups tied to a nation).</instruction>
        <input>2</input>
        <output>country_candidates</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Validate consistency: if all entities point to the same country, confirm it as the answer. If not, flag for further clarification.</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    
    <node id="5" type="output">
        <description>Return the identified country or an error if inconsistency is found.</description>
        <input>4</input>
    </node>