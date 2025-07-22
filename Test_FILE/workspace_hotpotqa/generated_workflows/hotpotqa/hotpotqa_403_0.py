# Workflow ID: hotpotqa_403_0
# Benchmark: hotpotqa
# Data Indices: [201, 2724, 1072, 94, 2872]

<node id="1" type="input">
        <param name="problem" value="self.problem"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify the key entities and relationships in the problem. Break down the question to find the specific target information needed.</instruction>
        <input>1</input>
        <output>entity_analysis</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Extract relevant context that directly relates to the target entity or event identified in step 2. Filter out irrelevant details.</instruction>
        <input>2</input>
        <output>filtered_context</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify if the filtered context contains a direct answer or requires further inference. If direct, return it; otherwise, proceed to infer based on logical connections.</instruction>
        <input>3</input>
        <output>answer_or_inference</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>If inference is required, trace the chain of evidence from the filtered context to logically derive the correct answer. Ensure no assumptions are made without support.</instruction>
        <input>4</input>
        <output>final_answer</output>
    </node>
    
    <node id="6" type="output">
        <input>5</input>
        <param name="result" value="final_answer"/>
    </node>