![[01_Async_System.png]]

* While our Base-Architecture seems wokring on paper it has some flaws and one if them is Separation of Concerns

In coding platforms like Leetcode contests are not the only thing it has  ,rather it has video tutorials , top 150 problems , most liked problems sheets etc etc . So it is made up of multiple set of features.now during the time of extreme load maybe not every single aspect of the application will face humongous amount of load.so during the contests are we going to see abrupt amount of scale from people buying subscription or solving those sheets or reading editorials etc.?No. so problem here is that if we put all of the logic in the one place if we scale the server for contest we are automatically scaling it for other features as well that do not need this amount of scaling.

All of the code modules like payments , users profile and registrations, submission,evaluator etc are inside one single server and running it as a single unit of server is nothing but a **Monolith Architecture** . Hence in Monolith architecture all the different business logic piece of code stays together and runs together.

#### Advantages

* If application is not complex like stack overflow . It is nothing but a quora for tech people.nothing but Question-Answer system with very basic disscussion [form](https://noncodersuccess.medium.com/stack-overflow-architecture-myth-vs-reality-93c77ec8d213).
* Stack overflow has humungous amount of scale but their business logic is straight forward and that's why Monolith works like charm in such cases.

#### Problems

* If we want to scale up say payment module only then we cannot do that because we have to scale all others as well.
* Monolith becomes unmanageable after a whlie.

*GOOGLE follows [MonoRepo](https://monorepo.tools/) Architecture* 

Instead of having all the modules inside the same project we can have payment module as a different project which would run in a different server on different machines altogether and same for all other modules as well is called **Microservices Architecture**.

#### Advantages

* One service's coding language can be very different from others.so maybe payment service is written in GO , Submission service is written in python and so on.
* Smaller projects to manage.Hene manageability becomes better.
* Any service can be scaled independently.

#### Problems

* Inside Monolith where every module is inside one big root then if say submission service had some dependency on payment service etc then these dependecnies could have been very easily resolved by using just a function call.but inside Microservices payment service has nothing to with submission service.so in this case if one microservice is dependent on other microservice then now we have to make a network call to have interaction between these services.
* Usually an overkill for smaller projects.


![[02_Optimized_Architecture.png]]

In 12th step we have to send the data back to Client effeciently 
* Server Sent Events (SSE)
* WebSocket

both are good in this usecase.

Benefit of websockets is it's duplex communication.but there's a limit to number of websockets connection that we can have while such is not the case with SSE.

so to manager our Websocktes we can introduce one more service named Socket Manager Service . 
* This service will always have a socket connection prepared with client and it will be separately horinzontally scaled if more connections are required.so usinng this way number of sockets connections needed will not impact the amount of scale Submission Service needs.

* Assume we have 1M clients and then we will have 1M socket connections running acrosss 5 different machines.so now how will we identify that submission with id 71 was made by which user ? so how do we know among those 1M requests which one of ther users we have to send the data to.
* so we assumed 1M user sent the submission request and one of the submission was evaluated now we want to know to whom this evaluated submission belongs to. As WebSocket connection is between two machines.It has nothing to do with User logic like user_id etc. So we have to setup a in-memory cache or persistent storage and inside that we have to maintain a user_id:socket_id mapping .So If a submission with user_id = 10 was a success we just lookup it's corresponding socket_id and this socket_id identfies the unique connection between the machine and the client's machine.

could we have used WebHooks here ? can our client expose an API ? our client is a web client and we cannot expose API there. But there is a usecase where webhooks can be used when our client is not a webclient just the way SPOJ does. so SPOJ is kinda Leetcode as a service.SPOJ says if you wanna build the Leetcode you do not have to build any Infra at all just send SPOJ the user submissions also tell it how to configure the test cases and SPOJ will run it on it's own machine . We just have to pay SPOJ nothing else.Back in the days CodeCheff used to use SPOJ so SPOJ would send the submission results to CodeCheff and then CodeCheff used to send the data back to user's browser.so in this CodeCheff server is not a web-client. So it makes a sense to use **WebHook**. WebHook are generally used with 3rd party Services interaction.

