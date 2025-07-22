# Workflow ID: drop_828_0
# Benchmark: drop
# Data Indices: [458, 58, 747, 1532, 3754]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements to extract from the passage.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Focus on specific details like names, numbers, or events mentioned in relation to the question.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify if the extracted information is sufficient to answer the question directly. If not, determine what additional context might be needed from the passage.</prompt>
    </node>
    
    <node id="4" type="decision">
        <prompt>Is the answer clearly present in the extracted information?</prompt>
        <yes>
            <node id="5" type="output">
                <prompt>Return the final answer based on the verified information.</prompt>
            </node>
        </yes>
        <no>
            <node id="6" type="agent">
                <prompt>Re-express the question in terms of the passage's structure (e.g., chronological order, categories, comparisons) to locate missing data.</prompt>
            </node>
            <node id="7" type="output">
                <prompt>Provide the answer after re-evaluation using structured reasoning.</prompt>
            </node>
        </no>
    </node>
    
    <connect from="1" to="2"/>
    <connect from="2" to="3"/>
    <connect from="3" to="4"/>
    <connect from="4" to="5"/>
    <connect from="4" to="6"/>
    <connect from="6" to="7"/>