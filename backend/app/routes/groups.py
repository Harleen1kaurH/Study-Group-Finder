"""
groups.py — study group routes.

Covers the full lifecycle of a study group: creation, discovery, membership,
and deletion. Only the group owner can update, delete, or remove members.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.course import Course
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import CreateGroupRequest, UpdateGroupRequest, GroupResponse
from app.services.notifications import notify_user, notify_group

router = APIRouter(prefix="/groups", tags=["groups"])


# Return all study groups, optionally filtered by course
@router.get("", response_model=list[GroupResponse])
def list_groups(course_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    query = db.query(Group)

    # Filter by course if provided
    if course_id is not None:
        query = query.filter(Group.course_id == course_id)

    return query.all()


# Create a new study group — logged-in user becomes the owner
@router.post("", response_model=GroupResponse)
def create_group(
    body: CreateGroupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Look up the course by code (case-insensitive)
    course = db.query(Course).filter(Course.code.ilike(body.course_code)).first()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with code '{body.course_code}' not found",
        )

    # Create the group with the logged-in user as owner
    group = Group(
        name=body.name,
        course_id=course.id,
        owner_id=current_user.id,
        max_size=body.max_size,
    )
    db.add(group)
    db.flush()  # get group.id before committing

    # Auto-add the owner as a member
    membership = GroupMember(group_id=group.id, user_id=current_user.id)
    db.add(membership)
    db.commit()
    db.refresh(group)
    return group


# Return details of a single group by ID
@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )
    return group


# Update group details — owner only
@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: uuid.UUID,
    body: UpdateGroupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Only the owner can update the group
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can update this group")

    # Update only the fields that were provided
    if body.name is not None:
        group.name = body.name
    if body.max_size is not None:
        group.max_size = body.max_size

    db.commit()
    db.refresh(group)
    return group


# Delete a group — owner only
@router.delete("/{group_id}")
def delete_group(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Only the owner can delete the group
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can delete this group")

    db.delete(group)
    db.commit()
    return {"message": "Group deleted"}


# Add the logged-in user as a member of the group
@router.post("/{group_id}/join")
def join_group(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Check if user is already a member
    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member of this group")

    # Check if the group is full
    member_count = db.query(GroupMember).filter(GroupMember.group_id == group_id).count()
    if member_count >= group.max_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group is full")

    # Add the user as a member
    membership = GroupMember(group_id=group_id, user_id=current_user.id)
    db.add(membership)
    db.commit()

    # Notify the user that they have been added to the group
    notify_user(
        db,
        user_id=current_user.id,
        type="member_added",
        message=f"You have been added to the group '{group.name}'",
        payload={"group_id": str(group_id)},
    )
    return {"message": "Joined group"}


# Remove the logged-in user from the group
@router.post("/{group_id}/leave")
def leave_group(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Owner cannot leave — they must delete the group instead
    if group.owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner cannot leave. Delete the group instead.")

    # Find and remove the membership
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not a member of this group")

    db.delete(membership)
    db.commit()
    return {"message": "Left group"}


# Remove a specific member from the group — owner only
@router.delete("/{group_id}/members/{user_id}")
def remove_member(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Only the owner can remove members
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can remove members")

    # Owner cannot remove themselves this way — use delete group instead
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself. Delete the group instead.")

    # Find and remove the membership
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
    ).first()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a member of this group")

    db.delete(membership)
    db.commit()

    # Notify the removed user
    notify_user(
        db,
        user_id=user_id,
        type="member_removed",
        message=f"You have been removed from the group '{group.name}'",
        payload={"group_id": str(group_id)},
    )
    return {"message": "Member removed"}
