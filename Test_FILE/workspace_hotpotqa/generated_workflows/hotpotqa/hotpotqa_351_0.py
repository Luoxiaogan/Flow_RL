# Workflow ID: hotpotqa_351_0
# Benchmark: hotpotqa
# Data Indices: [3077, 755, 3079, 3018]

<node id="1" type="input">
        <prompt>Understand the question and extract key entities.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Identify if the first entity is a rock band by checking its genre, style, and context.</prompt>
        <dependencies>1</dependencies>
    </node>
    
    <node id="3" type="agent">
        <prompt>Identify if the second entity is a rock band by checking its genre, style, and context.</prompt>
        <dependencies>1</dependencies>
    </node>
    
    <node id="4" type="agent">
        <prompt>Verify both entities are classified as rock bands based on their discographies and public recognition.</prompt>
        <dependencies>2,3</dependencies>
    </node>
    
    <node id="5" type="output">
        <prompt>Return a boolean answer indicating whether both entities are rock bands.</prompt>
        <dependencies>4</dependencies>
    </node>