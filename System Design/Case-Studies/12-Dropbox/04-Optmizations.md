- The basic architecture looks good for smaller file uploads but if we are looking for very big file like 50s or 100s of GB then we cannot rely on it and also sometimes there's limit to request body sent.
- Flow is synchornous everywhere if a file upload started and due to any reason it stops in between then we have to start from scratch.
- There are few more problems like we are uloading the file twice , once in FMS(first we upload it to this service) and then to s3 without any concrete reason. It wastes bandwidth and compute.

### Should we introduce CDNs here ?

- CDNs are expensive to manage and can incur extra cost but keeping them will improve the availability . As CDNs will keep the copy of the files close to geaographical regions of the user which will leads to lesser hop cross continent.
- We can use AWS cloudfront that integrates seamlessly with AWS services like S3, and has more than 310+ edge locations which will provide a better experience to the user.

![[Excalidraw/Drawing 2026-03-29 10.43.14.excalidraw]]

**Does AWS cloudfront provides different different URLs**
**for different edge location ?**

- It generally provides a single domain name that distributes across all edge locations worldwide.
- No separate URLs for edge location.
- You don't receive different URLs for different edge locations. CloudFront automatically re-directls the requests to the nearest edge location.
**Benefits**
- Simplified content delivery.
- Improved performance(reduced latency)
- Enhanced Security(SSL/TLS termination at edge location)

Edge location IP Address
- while we do not get different URLs but we can use tools like 
`dig command(distribution-domain-name) , nslookup , online tools like(cloudfront IP checker)` to get the IP address associated with specific edge location.

If we need more control over edge location

1. CloudFront Functions : Run custom logic at edge servers.
2. Lambda@Edge : Execute AWS lambda function at the edge location.
3. CloudFront Edge Group : Group edge locations for customized routing.

Keep In Mind
1. CloudFront's automatic edge location selection optimize performance.
2. Customization may add complexity and costs.

**Do we need to store every file on CDN ?**

- While CDNs will help improve the availability and lower down the latency it will also add more costs to us, so we can try and be smart here.
- Depending on the requirements of the app , if majority of the files are not going to be accessed across multiple regions and mostly users access their files from particular regions only and only a few files are there that are being accessed from a lot of user across globe then only these high demand files should be synced to the CDN.
- This will reduce the cost of CDN drastically , also we can ensure we replicate our architecture across multiple regions , as S3 is a regional service , we can make sure that user's of a particular regions have their files stored in the S3 bucket of their region only.
- For disaster recovery , we can keep the replica of the s3 buckets in multiple regions but this can happen async and can be directly based on the traffic.This also improves the availability.

![[Excalidraw/Drawing 2026-03-29 11.09.33.excalidraw]]


**Can we improve multiple clients uploading new files ?**
- AWS S3 provides notification on different events made to S3 buckets which are received on AWS SQS/SNS/Lambda
- We can have pub-sub architecture setup in a place,such that any updates made by some client once gone through S3 is published and other clients can subscribe to the same.
- This will improve short/long polling made by clients again and again because polling will add unnecessary load on DB as we are using DB timestamp to check for the updates.
- If we realtime updates as subscribers then we can use websockets but maintaining so many websockets can also add overhead and if this is contraint we can also opt in for add Redis realtime PubSub.
- If we do not want absolute realtime updates then AWS Lambda after receiving the notification can add an entry inside the Kafka topic, which can be subscribed.

![[Excalidraw/Drawing 2026-03-29 11.25.06.excalidraw]]
> SQS is before Kafka here because S3 pushes it's notification directly to SQS only.

