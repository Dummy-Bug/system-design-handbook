## Functional 

1. Upload files to the platform
2. Download files from the platform
3. Sync files on cloud across devices
4. Any file type
5. How internal blob storage is working (Out of scope)


## Non Functional

1. We need to support as low latency as possible.
2. Support a configurable max size upload with resumable uploads
3. Availability is more important than consistency. we can live with the fact that if we deploy our system across multiple regions then maybe someone accessing the system in different region sees the changes after a few seconds but we want to make sure that all functional capabilities of the system are always working i.e upload and download.

> It's a storage system so we must have replication in such type of systems in order to provide the druability. If user has uploaded something on dropbox then must never lose that data If we are using something like AWS then we should have a cross region replication.

so it's okay if I upload something to dropbox or drive and someone sitting in USA received the same file on drive after 10 seconds but it should never happen that USA sitting user is able to see the file but file is not downloading or uploading .Hence we can opt in for availbility and eventual consistency and for eventual consistency we can have the sync process to clone the data across multiple regions.

4. High data integrity is priority , sync accuracy is high with eventual consistency i.e once the data is synced we should not lose any data.

## Estimations

100M total users and 1M Dau

