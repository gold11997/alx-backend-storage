#!/usr/bin/env python3
""" returns all students sorted by average score"""


def top_students(mongo_collection):
    """
    The top must be ordered
    """
    return mongo_collection.aggregate([
        {"$project": {
            "name": "$name",
            "averageScore": {"$avg": "$topics.score"}
        }},
        {"$sort": {"averageScore": -1}}
    ])
