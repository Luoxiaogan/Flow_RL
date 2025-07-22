# Workflow ID: hotpotqa_44_0
# Benchmark: hotpotqa
# Data Indices: [3039, 89, 2887, 2334]

<operator id="1" type="agent">
        <instruction>Identify the key elements in the question: the film, the director, and the actor. Determine which film matches the description of being an upcoming American computer-animated epic musical drama directed by Jon Favreau.</instruction>
        <input>problem</input>
        <output>film_candidate</output>
    </operator>
    
    <operator id="2" type="agent">
        <instruction>Verify if the candidate film is indeed an upcoming American computer-animated epic musical drama directed and co-produced by Jon Favreau. Cross-check with known facts about Jon Favreau's work to confirm the match.</instruction>
        <input>film_candidate</input>
        <output>confirmed_film</output>
    </operator>
    
    <operator id="3" type="agent">
        <instruction>Once the film is confirmed, identify the source material for that film. Determine whether it is based on a book, a previous film, or another adaptation.</instruction>
        <input>confirmed_film</input>
        <output>source_material</output>
    </operator>
    
    <operator id="4" type="agent">
        <instruction>Find the author of the source material. This may involve checking the original story inspiration or adaptation credits, especially if the film is based on a classic or prior work.</instruction>
        <input>source_material</input>
        <output>author</output>
    </operator>
    
    <operator id="5" type="agent">
        <instruction>Final verification: Ensure that the author identified is correct by cross-referencing with reliable sources such as official film credits, production notes, or published interviews related to the project.</instruction>
        <input>author</input>
        <output>final_answer</output>
    </operator>
    
    <connect from="1" to="2"/>
    <connect from="2" to="3"/>
    <connect from="3" to="4"/>
    <connect from="4" to="5"/>