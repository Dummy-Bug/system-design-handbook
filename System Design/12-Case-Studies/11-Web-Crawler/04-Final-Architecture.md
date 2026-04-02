There would be cases where we are not able to parse all the urls
like site was not available because site was getting deployed or something for such type of cases then we should retry with a exponential backoff and in case if there are multiple failures for same url then we should have a mechanism of Dead Letter Queue

![[Excalidraw/Drawing 2026-03-27 14.28.37.excalidraw]]

sometimes some website can be more than 1MB so we might want to avoid them , We can use `content-length` header, instead of directly hitting the website direectly we can first make a `Head method` call which would return us the headers and we can check the content-length or any other header using which we can derive the content size if allowed then we can make the get request else skip.

other scenario could be there's page say wikipedia/google and inisde this we also have wikipedia/google , so possibility of infinite recursion is possible here, so we can use depth feature , so we can go till the depth of 30 urls only. we can optimize even further if last crawl url is under certain age we can skip it.