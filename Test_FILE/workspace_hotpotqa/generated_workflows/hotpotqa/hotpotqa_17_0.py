# Workflow ID: hotpotqa_17_0
# Benchmark: hotpotqa
# Data Indices: [3489, 1019, 596, 302, 2049]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements to compare.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Step 1: Extract relevant entities from the context for each part of the question. Think carefully about which entities are directly related to the comparison being asked.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Step 2: For each entity, determine the common genre or category they belong to. Focus on shared characteristics rather than individual traits.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Step 3: Compare the genres/categories identified in step 2. Determine if there is a single overlapping genre that applies to both entities.</prompt>
    </node>
    
    <node id="5" type="agent">
        <prompt>Step 4: If a common genre exists, confirm it by cross-checking with the definitions provided in the context. Ensure no misinterpretation of terms occurs.</prompt>
    </node>
    
    <node id="6" type="output">
        <prompt>Final answer: Provide the genre that both entities share based on your analysis.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>