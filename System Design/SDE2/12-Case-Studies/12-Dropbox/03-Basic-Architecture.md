## Upload flow

![[Excalidraw/Drawing 2026-03-27 19.42.00.excalidraw]]

- Client sends the request to API GAteway (can be managed by AWS) for uploading the file.
- This upload request is routed to file management service.
- Now inside upload file request we are sending the file and file metadata and both of these needs to be stored as lot of time users might just want to see file related details instead of complete file content.(e.g when listing their bookmark files)
- Now both file and file matadata should not be stored in the same type of DB why ? because traditional DBs like RDBMS or key value store are not optimized to store huge file data , also the file can be music , image , pdf etc . Hence we are storing it inside BLOB(Binary Large Object) storage.
- Some DBs have mechanism of storing BLOB as well but a better way would be to use some managed Blob storage provider like AWS s3.
- Now our FMS takes the upload file andstore it inside s3 and s3 will return the link through which we can access the file.
- Eventually we update the MetaData DB with with the new S3 link 

## Download Flow


![[Excalidraw/Drawing 2026-03-28 09.34.22.excalidraw]]

- Download flow is self explanatory

# Sync Flows

## Remote changed and cient needs to sync

![[Excalidraw/Drawing 2026-03-28 10.35.41.excalidraw]]
- For the sync case where remote has updated but client is not then we can have periodic long polling mechanism where the client will raise the request of getting changes

> For now we are going with the basic solution that let's say if a device has to get the latest data of all the files or sync the files client or user can decide at what frequency get the backup updates.like every 5 minutes user want to sync and that's why Long Poiiling has been chosen. This is a pull based mechanism.

- We will keep the separate microservice File Syncing Service(FSS) which will receive the sync request with file_id and last_updated_at timestamp from the client.
- It will make a query to DB and check if last updated timestamp is different than updated_at timestamp in the DB then it will respond with complete file metadata or maybe just with the s3 link(to keep the payload smaller).
- Then the client can use the s3 link from the response to download the the latest content and if there is no change then we can indicate with a response code to client that there is no update.
- Keeping a separate FSS ensure that if we have lot of load on the system then upload can stay unaffected from the sync and we can maybe delay the syncs as we are only looking for eventual consistency.

## Local changed and remote needs to sync

![[Excalidraw/Drawing 2026-03-28 12.46.27.excalidraw]]
- In cases when remote is behind the local changes we need to trigger an upload of the new content 
- To check if any change has been done to file or not we can use OS level watcher APIs to make sure that we get a trigger whenever a file is changed
- Once updated then we will raise the synchChnages request to FSS , which can reuse upload logics from FMS to upload a new file content and get the new s3 link.
- We can also extend this change to maintain history of changes , so we just need to store the series of links from s3 from old changes.


