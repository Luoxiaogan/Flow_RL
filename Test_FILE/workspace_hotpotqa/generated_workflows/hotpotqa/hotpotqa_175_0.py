# Workflow ID: hotpotqa_175_0
# Benchmark: hotpotqa
# Data Indices: [745, 665, 3569, 1739]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the key entities.</prompt>
        <dependencies>1</dependencies>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question or requires further processing.</prompt>
        <dependencies>2</dependencies>
    </node>
    
    <node id="4" type="agent">
        <prompt>If indirect, trace relationships between entities to derive the answer logically.</prompt>
        <dependencies>3</dependencies>
    </node>
    
    <node id="5" type="output">
        <prompt>Provide the final answer based on the processed information.</prompt>
        <dependencies>4</dependencies>
    </node>