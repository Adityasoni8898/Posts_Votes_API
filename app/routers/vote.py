from .. import schemas, models, oauth2, database
from fastapi import HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), curr_user:int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} not found")
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == curr_user.id)
    found_vote = vote_query.first()
    if(vote.direction == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{curr_user.id} have already voted")
        else:
            new_vote = models.Vote(post_id = vote.post_id, user_id = curr_user.id)
            db.add(new_vote)
            db.commit()
            return {"message": "Vote added"}
    else :
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{curr_user.id} have not voted")
        else:
            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message": "Vote removed"}