
```Http

[Web Client] --->[Load Balancer] ---> [App Server] ---> [DB]
```

* App Servers are Horizontaly scaled.

so assume from the web-client user has submitted the code.
so for every request we would have the following 


POST /api/v1/submissions

```Json

{
	user_id,
	problem_id,
	code_language,
	code,
}
```

* It's a good idea to get user_id from the token instead of accepting it from the request 

so what happens once this request reaches the App Server?

1. We need to register the user's code submission inside the DB with status PENDING.

	SUBMISSON schema
	```Json
	
	id,
	status : TLE/MLE/WRONG/PENDING/SUCCESS
	code_language : cpp/c/java/python
	createdAt,
	user_id,
	problem_id,
	contest_id,
	```
	
	But when we have to register the request in the database , what type of request this should be ?
	
	can we just say that from the App Server we would just send the request and maybe not wait for the acknowledgment but this is not the correct way as it might be possible that DB is crashed ,maybe DB is not working . so if we want to ensure that user's submission has been successfully added as an entry in the database we have to wait for an acknowledgment to come up from the DB. This kind of communication is **Synchronous** communication because we are waiting for the response to come up.

2. Evaluate the submission but where to evaluate the submission?

	we might be getting the CPP/JAVA/PYTHON code so we have to compile the code then we have to run the code and then we have to match it for the test cases of the problem.

	* The first natural instict is to have this logic present inside the App Server because it is a stateless evaluation so whatever application server's instance accepted the request that App Server can evaluate the submission.
	
   but should we run the code provided by user directly on our App Server ? what if someone provided the [**Fork Bomb**](https://www.imperva.com/learn/ddos/fork-bomb/)? and other problem is even if code from user is not malicious but what if it takes too much time ? on Leetcode just after a submission we can submit again and again just after our previous submissions. Like first submission is not completely evaluated but you have started the second submission and then third and so on. and it does not matter for same problem or different problems. because compiling and running and then checking it for all the test cases is a time consuming task. 
   
	so we cannot afford the user to get blocked .we have to block the user till the submission is recorded inside the DB after that we have the submission inside the DB now we can let the user perform any task he wants and behind the scenes we have to evaluate this submission from the user.

	```Json
	
[Web Client] <--- [Load Balancer] <--- [App Server] <--- [DB]	
	```

	Hence as soon as we get the acknowledgement from the DB the App Server would immediatley respond back to the user saying hey we have recorded the submission and we are evaluating your submission and once it's done you will be notified. so This type of communication is **Asynchronous** communication because is not blocked for the code's evaluation.

	so we have returned the response to the user but still we have to evaluate the submitted code and even if we have another **Evaluator Machines** whose task is to evaluate a submission the risk of Fork Bomb is still there . so in order to solve such a problem we have to use some kind of **Virtual machine** or **Docker** . so in this Evaluator machine we will run a small virtual machine(VM).Now user's submitted code would run on this VM and not directly on the actual Evaluator machine or App server now even if Fork Bomb is present only the VM running the Fork Bomb would go down instead of whole machine or servers.so inside the docker containers we can have multiple VMs evaluating multiple submissions. so we can have multiple horizontally scaled Evaluator machines as well as each Evaluator machine can run multiple VMs making our system highly available.
	
	but booting up a docker container is time consuming task. and then on top of that we have to compile , run and evaluate against test case the submission itself. Users while attempting the contest keep on submitting the solution they do not think that Leetcode's infra might go down etc etc and why would they. so we cannot allow our App Server to bombard submissions on Evaluate machines because contnuous bombardment of submissions on Evaluator machines would crash.
	
	* The natural solution is autoscaling but the problem with this is there would be request of lot of machines.
	* Even if we rate limit then we can apply a rate limiting for a particular user say in one minute user is allowed to make only one submission.but what if there are 1M users in the contest itself.5 request per user per minute we have 5M request per minute means 5m evaluations which is insanely high. 
	* Every submission should be evaluated in a different docker container. say we are evaluating 5 different submissions and one of them contains the Fork Bomb then it can impact other submissions as well.So every submission would be having it's own Docker container and every container would be having different image based on the language that we want.

	so we can keep horizontally scaled Evaluator machines but we have to setup a mechanism with which the whole asynchronous communication can work.

	We have to park our request means not every request is needed to evaluate immediatley so that whenever the load is manageable we can evluate the parked requests. The moment we realize that some system requires parking of requests best way is to use some kind of Message Broker likes of RabitMQ , SQS , KAFKA(it's more than a message broker more on this later).

	Imagine a scenario we have service s1 that is capable of making 1000 request per sec to some other service s2 but the capacity of s2 is only 10 request per second. so s2 is left with only two choices
	* Accept only the 10 requests in some fashion(fcfs or ) and discard other requests.
	* Or it can park the requests so it is kinda telling s1 you are sending me 1k requests that's good I will process every request but i will not give you the results immediatley so resopnse would be according to s2's load handling capacity.
	* Here s1 is a producer who is producing lot's of data and s2 is a consumer who is not able to keep up with the pace of a producer then parking the request is a good way.

	Hence our App Servers are going to create a submission request or add submissions payloads inside these queues and that's it .Now inside the Evaluator machines we have to run the consumer's code or also known as job processor code. 

	Now different different queues can be used like in contest FCFS is obvious but for normal Leetcode problems two submissions are present inside the queues but first one is normal user's submission and second one is permium user's submission then paying user should get the priority so we have to user Priority Queues. or we can have a mechanism such that all the paid user submissions goes to q1 and normal users submissions goes to q2. and any request coming to the q1 would be evaluated first.

	We would be focusing only on contest scenario only. assuming queue has 4 jobs and assuming we have only one Evaluator machine we have not horizontally scaled it as of yet and also assume one Evaluator machine is capable of running 3 VMs only so only 3 parallel evaluations are possible . so out of 4 jobs 3 jobs would be run in parallel inside VMs and 4th one has to wait till the job processor(any of the VMs) is free again. but what happens once the evaluation is completed ? how to contact the App server as it is not waiting anymore it just added the submission payload and did not wait for any acknowledgement or something anymore. so once any submission has been evaluated it's Evaluator machines job to produce the evaluation result and put it inside the Evaluator Queues. and then App Server has to consume it and once consumed it has to update the entry inside the DB as it has to update the evaluation status of the submitted problem.
	
	Any entry that we are making in the queue is generally called as submission or job or payload and the piece of code that reads the job and gets the task done is called **Job Processor** .

	Now if we are expecting lot's of user submission bombardments we can simply horizontally scale these queues and similarly we can scale our Evaluator machines as well. So this solves are most of the problems.

	Ever Wondered how TLE and MLE are evaluated ? Docker allows us to restrict the amount of memory our container is having.If the code is taking more memory than the memory allocated to the docker container then Docker container would give us the response that you are out of memory.

	what about the Test cases ? most of the times test cases are static files because problem setter has created the test cases and we generally store it inside the Blob storage like S3 for both input and output test cases. so these docker containers can communicate with AWS S3 , download the test cases , do the evaluation and do the text matching etc such that the output generated by user's code is matched with the output expected from the output test cases.but why are we keeping the test cases inside S3 ? because one problem can have say 100 test cases for all the 100 test cases we have both input and outputs so 200 text files per problem.so let's say we have only 1k problems then 10^3* 200 and inside each text file we will be having lot of data. so our normal DBs are not that much optimized to keep these kind of files.like mongoDB provides the functionality to save files in DB as well but there's an upper limit.


### Problems

* App Server added the entry inside the queue but it was never read by the Evaluator machine because Queue server went down.

so what happens to that entry once the Queue is back ?
* **Atleast One** If a job was added to the Queue then atleast one Job Processor would be able to consume it . 
* **At Most One** If a job was added to the Queue then only one processor would be able to read it.

In our case at most one is good enough for us.

so as of now the flow is App server would receive the submission request then it will save the entry inside the DB and wait for acknowledgment and then add the submission payload inside the Queue and then return the response to user that submission has been recorded and will be notified to you once it's evaluated .

but what if instead of waiting for the acknowledgement App Server add the payload inside Queue parallel to making entry inside the DB. If we do this then when control reaches the Evaluator machine and it starts to read the data then inside those machines first system have to interact with the DB to check if the entry is present inside the DB or not. 
* but if not added for any failure or anything but it was recorded inside the Queue then at that point of time we create the entry inside the DB(but for this we have to handle other cases as well because of the DB was down then App Server would have send back the response to user that not able to record your submission and all). 
* Other scenario is if entry is not present we do not evaluate it and we requeue it back like we add it again inside the Queue from Evaluator machine for a retry. and even after multiple retrues if the entry is still not there inside the DB then we can just discard the submission.

![[01_Async_System.png]]


   
   
   
