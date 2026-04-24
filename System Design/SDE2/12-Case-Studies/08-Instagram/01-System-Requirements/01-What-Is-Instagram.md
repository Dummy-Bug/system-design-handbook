# What is Instagram?

Instagram is a social media platform where users share photos, videos, and short-form clips (Reels), follow other users, and consume a personalized feed of content. The home feed shows posts from people you follow; the Explore feed surfaces content you haven't seen before, personalized to your interests based on past likes, views, and searches. Stories are ephemeral — they disappear after 24 hours.

What makes Instagram an interesting design problem is not the feature set — it's the scale. At 2 billion monthly active users, when a celebrity with 50 million followers posts a photo, up to 50 million feed entries need to be updated. The central tension in the design is **fan-out**: do you push content to every follower's feed at write time (fast reads, expensive writes), or do you pull and assemble feeds at read time (cheap writes, slow reads)? Getting this tradeoff wrong at Instagram's scale means either feeds that lag by minutes or write pipelines that collapse under celebrity posts.

> [!info] Why this question is asked at SDE-2
> Instagram is the canonical **Live News Feed** problem. The fan-out on write vs fan-out on read decision is one of the most frequently tested design tradeoffs at Google L4. Every other decision in the system — DB choice, caching strategy, sharding — flows from which fan-out model you pick.
