from django.core.management.base import BaseCommand
from octofit_tracker.models import User, Team, Activity, Leaderboard, Workout
from django.conf import settings
from pymongo import MongoClient
from datetime import timedelta
from bson import ObjectId
import json

class Command(BaseCommand):
    help = 'Populate the database with test data for users, teams, activities, leaderboard, and workouts'

    def handle(self, *args, **kwargs):
        # Connect to MongoDB
        client = MongoClient(settings.DATABASES['default']['HOST'], settings.DATABASES['default']['PORT'])
        db = client[settings.DATABASES['default']['NAME']]

        # Drop existing collections
        db.users.drop()
        db.teams.drop()
        db.activity.drop()
        db.leaderboard.drop()
        db.workouts.drop()

        # Load test data from JSON file
        with open('octofit_tracker/test_data.json') as f:
            data = json.load(f)

        # Remove duplicate users before inserting new data
        existing_usernames = set()
        for user in User.objects.all():
            if user.username in existing_usernames:
                user.delete()
            else:
                existing_usernames.add(user.username)

        # Ensure unique usernames during user creation
        for user_data in data['users']:
            User.objects.update_or_create(username=user_data['username'], defaults=user_data)

        # Populate teams
        for team_data in data['teams']:
            team = Team.objects.create(**team_data)
            team.save()

        # Populate activities
        for activity_data in data['activities']:
            user = User.objects.get(username=activity_data.pop('user'))
            duration_str = activity_data.pop('duration')
            hours, minutes, seconds = map(int, duration_str.split(':'))
            activity = Activity.objects.create(user=user, duration=timedelta(hours=hours, minutes=minutes, seconds=seconds), **activity_data)
            activity.save()

        # Populate leaderboard
        for leaderboard_data in data['leaderboard']:
            user = User.objects.get(username=leaderboard_data.pop('user'))
            leaderboard = Leaderboard.objects.create(user=user, **leaderboard_data)
            leaderboard.save()

        # Populate workouts
        for workout_data in data['workouts']:
            workout = Workout.objects.create(**workout_data)
            workout.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data.'))
