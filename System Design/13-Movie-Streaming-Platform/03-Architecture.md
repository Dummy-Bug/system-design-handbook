- We have to store chunk files somewhere,these are end to end blob files so we can store them inside s3 blob storage and S3 also provide us the hierarchy such that we can have one bucket and inside it we can have multiple objects.so each bucket can be the resolution.
- But there's one more catch in order for all these .ts and .m3u8 files we also need original video uploaded somewhere.

**Uploading** can be solved in two ways

Assume we have a client and a app server and a storage , now for a moment assume that this storage is not inside anywhere else but inside the same application server . The problem would be that this application's server hard disk would get bloated with the very heavy uploads so it's not a very good idea to do so.So we have to keep storage out of our application server only
and what could be the better storage to store big video files than S3.

* From client we upload it to the server , server collects the file and upload it to the storage.This can be one of the way to upload any kind of file. The problem with this approach is we are kinda doing double upload , as the same video first is getting uploaded to server and then from server to storage. So we are consuming lot of bandwidth and lot of time.

what if our client can upload directly to storage in more secured way? Interestingly S3 and most of the blob storage do provide that mechanism.
- From client upload the metadata of the file to the server i.e what is the file all about, app server would take that metadata and submit it on S3 and S3 would return presigned URL.
 > A presigned url is a secured upload url which is available for a temporary amount of time and if a client has this url it can directly upload the same file for which client has sent the metadata to S3 storage.
 
 - So client would send the matadata to app server which it would send further to S3 which would reply back with presigned url which would propgated through app server to client and then client can use this short lived url to directly upload the big ass file to S3 directly.

> Instead of uploading whole file using presigned URL we can upload chunk by chunk and we can also implement resumable upload such that even if upload stops due to some network or internet issue it can be resumed from that chunk.This type of chunk by chunk upload is also done on the platform like torrents.

So with this let's design basic system using presigned URL
![[Excalidraw/Drawing 2026-03-31 21.40.33.excalidraw]]

**API**
/POST api/v1/video/fetchpresignedurl
{video_metadata:{}}

we have to use DB to store video metadata,we can use any DB as we won't be having those many writes and if data looks unstructued so mongDB is okay for us.

The moment video has been uploaded to the S3.It has event notification feature,so we do not have to poll S3 again and again so it can actually sends event notification to a dedicated video processing system. Once the video processing pipeline is done we can have a state of the video inside the DB , and we can mark the state to `processed` then all the processed chunk etc can be re-uploaded back to S3.


Once the video chunks has been created and stored inside S3 , what can we do to improve to optimize the Reads ? as video uploaded once would be viewed by millions of users.

- We can improve Reads by using caching but caching of these files can be tricky till now whatever type of caching we have prepared that was some kinda preemptive or non preemptive object.but we have never cached complete end to end asset or a video or a very big blob file.That's where the concept of CDNs comes into the picture.

## CDN

Expectation of a user is that as soon as he start the streaming he should see the video.
- We can do asynchronous cross region replication on S3 ,so users from India would be served from Mumbai and from users from USA would be served from say New York(assuming we have servers there).But still we have to fetch the video from S3 only.

> [CDN](https://aws.amazon.com/what-is/cdn/) stands for Content Delivery/Distribution Network.It is a type of a cache that uses distributed servers to deliver contents based on their geographical locations and CDNs are very much optimize to deliver these kinds of dynamic assets like images,videos etc. So content is getting cached at the servers that are even closer to the clients which we call as **Edge Servers**.CDNs are not just for static assets.If a new episode of a webseries has released then we can put that into CDN as well.

so we can upload the data to CDN like Amazon cloudfront.so whenever client starts streaming they can directly stream from CDN itself.

CDN is working as a caching layer for heavier files and we can also decide when to remove the data from the CDNs.We want our data to be heavly cached as we do not want every user to bombard our S3 servers etc.Our S3 would act as a fault tolerance system because let's say CDN goes down then still the data would be inside S3 and we can start serving things from S3.

[Netflix uses the machines of ISPs to act as a CDN for them](https://about.netflix.com/en/news/how-netflix-works-with-isps-around-the-globe-to-deliver-a-great-viewing-experience)


