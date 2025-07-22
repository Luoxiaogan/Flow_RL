# Workflow ID: hotpotqa_91_0
# Benchmark: hotpotqa
# Data Indices: [125, 1266, 588, 362]

<node id="1" type="input">
        <description>Receive problem context and question</description>
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify key entities and relationships in the context. Extract relevant facts that directly answer the question.</instruction>
        <dependencies>1</dependencies>
    </node>
    
    <node id="3" type="agent">
        <instruction>Compare extracted facts against possible answers. Determine which entity matches the criteria specified in the question.</instruction>
        <dependencies>2</dependencies>
    </node>
    
    <node id="4" type="agent">
        <instruction>Validate the match by cross-referencing with additional context clues to ensure accuracy.</instruction>
        <dependencies>3</dependencies>
    </node>
    
    <node id="5" type="output">
        <instruction>Return the final answer based on validated evidence.</instruction>
        <dependencies>4</dependencies>
    </node>