# Workflow ID: hotpotqa_341_0
# Benchmark: hotpotqa
# Data Indices: [1750, 2960, 2213, 1858, 3314]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the question. Focus on performers at Stand-Up New York and their associations with Comedy Central shows.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Identify which comedian from Stand-Up New York is featured in a Comedy Central show. Cross-reference known performers and their TV appearances.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Verify that the identified comedian indeed performed at Stand-Up New York and is associated with a Comedy Central show. Ensure no ambiguity in the match.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the name of the Comedy Central show featuring the comedian who performed at Stand-Up New York.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>