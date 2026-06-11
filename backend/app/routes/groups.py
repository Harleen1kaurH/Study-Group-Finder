"""
groups.py — study group routes.

Covers the full lifecycle of a study group: creation, discovery, membership,
and deletion. Only the group owner can update, delete, or remove members.
"""

from fastapi import APIRouter
from app.schemas.group import CreateGroupRequest, UpdateGroupRequest, GroupResponse

router = APIRouter(prefix="/groups", tags=["groups"])


# Return all study groups (optionally filtered by course)
@router.get("", response_model=list[GroupResponse])
def list_groups():
    return {"message": "not implemented yet"}


# Create a new study group tied to a course
@router.post("", response_model=GroupResponse)
def create_group(body: CreateGroupRequest):
    return {"message": "not implemented yet"}


# Return details of a single group by ID
@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: str):
    return {"message": "not implemented yet"}


# Update group details — owner only
@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: str, body: UpdateGroupRequest):
    return {"message": "not implemented yet"}


# Delete a group and all its sessions — owner only
@router.delete("/{group_id}")
def delete_group(group_id: str):
    return {"message": "not implemented yet"}


# Add the logged-in user as a member of the group
@router.post("/{group_id}/join")
def join_group(group_id: str):
    return {"message": "not implemented yet"}


# Remove the logged-in user from the group
@router.post("/{group_id}/leave")
def leave_group(group_id: str):
    return {"message": "not implemented yet"}


# Remove a specific member from the group — owner only
@router.delete("/{group_id}/members/{user_id}")
def remove_member(group_id: str, user_id: str):
    return {"message": "not implemented yet"}
