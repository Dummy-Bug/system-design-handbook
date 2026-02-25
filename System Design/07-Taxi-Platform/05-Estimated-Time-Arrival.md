* Simplest of the ways is to directly call the Google maps APIs and get the ETA but it's not an optimized way to do it for large scaled application like ours. It's good when let's we are making the app ourselves till the scale is not that huge Google maps APIs are the perfect.


#### Shortest Path Algorithms

* We could have taken A* algorithm as well but Dijkstra is a bit easier to explain in the interview just in case if interviewer goes in depth of the algorithm itself.

The only tricky part in shortest pair algorithm is what would be the Vertices or Nodes and what would be the Edges ?

* **Edges** are simply the roads.
* **Nodes** are nothing but intersection of the roads.

for example I want to go from point A to point B

A-----------B 

now assume there's a junction between A and B named J

         C
         .
         .
         .
A..... J .....B 
         .
         .
         .
         D

and from J we can go to A , B or C and D.

so AJ is an edge , CJ , JD and JB are also the edges.

and since we have now the Nodes and Edges now we can easily apply shortest path algorithm.

so now we will add traffic also and traffic would be associated with the weight of the graph. so we will use GRAPH DB here which would constantly be getting updated say from going A to J it took me 5 minutes then inside the GRAPH DB the weight of the edge AJ would be updated correspondingly.now let's say after few minutes traffic gets better now it is taking only 2 minutes to travel from A to J then it will be updated the same inside teh DB as well meaning the weight of the edge will also get dwindle.

How can we calculate the edge weights more effeciently ?

W = length of the segment / assumed average speed on road
now for each type of road (Highway , Expressway ,City road) we can have different assumed average speed.

Traffic data can be gathered from the driver's devices , the density of the vehicle on the route . There's google map's traffic api aslo. open traffic apis are present as well .

so open street map apis would tell us like in which places the intersections are present and where all roads are present.Then government road dataset also provides the detailed road network data. and then we build te graph on top of it .

