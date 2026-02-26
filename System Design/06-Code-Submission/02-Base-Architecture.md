
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
	
	but booting up a docker container is time consuming task. and then on top of that we have to compile , run and evaluate against test case  the submission itself.

   
   
   
