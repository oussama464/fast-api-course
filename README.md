# votings/likes System Requirements

- users should be able to like a post
- should only be able to like a post once
- Retrieving posts should also fetch the total number of likes

---

- path will be at "/vote"
- the user id will be extracted from the JWT token
- the body will contain the id of the post the user is voting on as well as the direction of the vote
  {
    post_id:1234,
    vote_dir:0
  }

- a vote direction of 1 means we want to add a vote, a direction of 0 means we want to delete a vote
